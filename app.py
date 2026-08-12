from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
import os

app = Flask(__name__)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# In-memory history — the "active array" that gives this chatbot memory
history = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/reset", methods=["POST"])
def reset():
    history.clear()
    return jsonify({"status": "cleared"})


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()

    # Structural Validation Gate — block empty input before it reaches the API
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Step 1: Ingest & Append — add the user's message to history
    history.append({"role": "user", "content": user_message})

    # Step 2: Transmit — build a chat session from EVERYTHING so far, then send
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

    # Step 3: Record — append the reply too, so next turn remembers it
    # Step 3: Record — append the reply too, so next turn remembers it
    history.append({"role": "assistant", "content": reply_text})

    # Sliding window — keep memory from growing forever (last 20 turns)
    while len(history) > 40:
        history.pop(0)

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)