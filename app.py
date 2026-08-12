from flask import Flask, render_template, request, jsonify, session
from google import genai
from google.genai import types
from datetime import datetime, timedelta
import os
import uuid

app = Flask(__name__)

# SECRET_KEY signs the session cookie that identifies each visitor.
# Set this as an environment variable on Render so it stays stable across restarts
# (otherwise everyone gets logged out / loses their chats whenever the server restarts).
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24).hex())
app.permanent_session_lifetime = timedelta(days=30)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# In-memory storage, scoped per user:
# all_chats = {
#   user_id: {
#     chat_id: {"title": str, "messages": [...], "created": iso_timestamp}
#   }
# }
all_chats = {}


def get_user_id():
    """Every browser gets its own persistent, private user_id via a signed cookie."""
    session.permanent = True
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return session["user_id"]


def get_user_chats(user_id):
    return all_chats.setdefault(user_id, {})


def ensure_current_chat(user_id):
    """Make sure there's an active chat_id for this user; create one if needed."""
    chats = get_user_chats(user_id)
    chat_id = session.get("current_chat_id")
    if not chat_id or chat_id not in chats:
        chat_id = str(uuid.uuid4())
        chats[chat_id] = {
            "title": "New chat",
            "messages": [],
            "created": datetime.utcnow().isoformat(),
        }
        session["current_chat_id"] = chat_id
    return chat_id


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chats", methods=["GET"])
def list_chats():
    """Sidebar data: list of this user's saved chats, newest first."""
    user_id = get_user_id()
    chats = get_user_chats(user_id)
    result = [
        {"id": cid, "title": c["title"], "created": c["created"]}
        for cid, c in sorted(chats.items(), key=lambda kv: kv[1]["created"], reverse=True)
    ]
    return jsonify({"chats": result, "current_chat_id": session.get("current_chat_id")})


@app.route("/chats/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    """Load one saved chat's full message history (used when clicking it in the sidebar)."""
    user_id = get_user_id()
    chats = get_user_chats(user_id)
    if chat_id not in chats:
        return jsonify({"error": "Chat not found"}), 404
    session["current_chat_id"] = chat_id
    return jsonify({"messages": chats[chat_id]["messages"], "title": chats[chat_id]["title"]})


@app.route("/new_chat", methods=["POST"])
def new_chat():
    """Start a fresh chat. The old one is already saved in all_chats, so nothing is lost."""
    user_id = get_user_id()
    chats = get_user_chats(user_id)
    chat_id = str(uuid.uuid4())
    chats[chat_id] = {
        "title": "New chat",
        "messages": [],
        "created": datetime.utcnow().isoformat(),
    }
    session["current_chat_id"] = chat_id
    return jsonify({"chat_id": chat_id})


@app.route("/chat", methods=["POST"])
def chat():
    user_id = get_user_id()
    chat_id = ensure_current_chat(user_id)
    chats = get_user_chats(user_id)
    history = chats[chat_id]["messages"]

    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Step 1: Ingest & Append
    history.append({"role": "user", "content": user_message})

    # First message of a chat becomes its sidebar title
    if chats[chat_id]["title"] == "New chat":
        chats[chat_id]["title"] = user_message[:40] + ("..." if len(user_message) > 40 else "")

    # Step 2: Transmit — build a chat session from this chat's history only
    gemini_history = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])]
        )
        for m in history[:-1]
    ]
    chat_session = client.chats.create(model="gemini-3.5-flash", history=gemini_history)
    response = chat_session.send_message(message=user_message)
    reply_text = response.text

    # Step 3: Record
    history.append({"role": "assistant", "content": reply_text})

    # Sliding window — keep each chat's memory from growing forever
    while len(history) > 40:
        history.pop(0)

    return jsonify({"reply": reply_text, "chat_id": chat_id, "title": chats[chat_id]["title"]})


if __name__ == "__main__":
    app.run(debug=True)
