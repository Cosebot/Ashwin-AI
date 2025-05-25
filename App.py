from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyD5nKn8-K4cV0Lnc1NmkpB_3uZv3pfBLz4"
GEMINI_API_URL = "https://api.gemini.ai/v1/chat/completions"  # Hypothetical URL

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Gemini AI Chat</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
    body { background:#0e0e0e; color:#fff; font-family:sans-serif; padding:20px; }
    .container { max-width:400px; margin:auto; display:flex; flex-direction:column; height:100vh; }
    textarea { width:100%; height:100px; margin-bottom:10px; padding:10px; font-size:16px; border-radius:10px; border:none; resize:none; }
    button { padding:12px; background:#1f8ef1; color:#fff; border:none; border-radius:10px; font-size:16px; cursor:pointer; margin-bottom:10px; }
    .response-box { flex:1; background:#1a1a1a; padding:10px; border-radius:10px; white-space: pre-wrap; overflow-y:auto; }
</style>
</head>
<body>
    <div class="container">
        <form method="POST">
            <textarea name="prompt" placeholder="Type your prompt...">{{ prompt or '' }}</textarea>
            <button type="submit">Send</button>
        </form>
        <div class="response-box">{{ response or 'Response will appear here...' }}</div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    prompt = ""
    response = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        if prompt:
            headers = {
                "Authorization": f"Bearer {GEMINI_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "gemini-1-chat",
                "messages": [{"role": "user", "content": prompt}]
            }
            try:
                res = requests.post(GEMINI_API_URL, json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                # Typical response format assumed:
                response = data['choices'][0]['message']['content']
            except Exception as e:
                response = f"API call failed: {str(e)}"

    return render_template_string(HTML, prompt=prompt, response=response)

if __name__ == "__main__":
    app.run(debug=True)