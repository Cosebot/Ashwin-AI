from flask import Flask, request, render_template_string, jsonify
from transformers import pipeline

app = Flask(__name__)

# Load the pre-trained base conversational model (no fine-tuning)
chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Base Chatbot</title>
<style>
  body {
    margin: 0; padding: 20px;
    font-family: Arial, sans-serif;
    background: #121212; color: #eee;
    display: flex; flex-direction: column; height: 100vh;
  }
  .container {
    margin: auto; max-width: 400px;
    width: 100%; display: flex; flex-direction: column; height: 100%;
  }
  textarea {
    width: 100%; height: 100px;
    resize: none; padding: 10px; font-size: 16px;
    border-radius: 8px; border: none; outline: none;
    margin-bottom: 10px;
  }
  button {
    padding: 12px; font-size: 16px;
    background: #0066ff; color: white; border: none; border-radius: 8px;
    cursor: pointer; margin-bottom: 10px;
  }
  .response-box {
    flex: 1; overflow-y: auto;
    background: #222; padding: 10px; border-radius: 8px;
    white-space: pre-wrap;
  }
</style>
</head>
<body>
  <div class="container">
    <form id="chat-form">
      <textarea id="prompt" placeholder="Type your message here..."></textarea>
      <button type="submit">Send</button>
    </form>
    <div class="response-box" id="response">Response will appear here...</div>
  </div>

<script>
  const form = document.getElementById('chat-form');
  const promptInput = document.getElementById('prompt');
  const responseBox = document.getElementById('response');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = promptInput.value.trim();
    if (!prompt) return;
    responseBox.textContent = "Waiting for response...";
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt})
      });
      const data = await res.json();
      if (data.response) {
        responseBox.textContent = data.response;
      } else {
        responseBox.textContent = data.error || "Unknown error";
      }
    } catch (err) {
      responseBox.textContent = "Request failed: " + err.message;
    }
  });
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    try:
        result = chatbot(prompt)
        # result is a list of conversations, get the last generated text
        answer = result[0]['generated_text'] if result else "No response"
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)