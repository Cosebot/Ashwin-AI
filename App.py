from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

DEEPSEEK_API_KEY = "sk-0e1fd86d884a44be816fdbcd8c8a365d"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DeepSeek Chat</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: sans-serif;
            background: #0e0e0e;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            height: 100vh;
            box-sizing: border-box;
        }

        .container {
            max-width: 400px;
            margin: auto;
            width: 100%;
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        textarea {
            width: 100%;
            height: 100px;
            resize: none;
            padding: 10px;
            font-size: 16px;
            margin-bottom: 10px;
            border-radius: 10px;
            border: none;
            outline: none;
        }

        button {
            padding: 12px;
            background: #1f8ef1;
            color: white;
            border: none;
            font-size: 16px;
            border-radius: 10px;
            cursor: pointer;
            margin-bottom: 10px;
        }

        .response-box {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            background: #1a1a1a;
            border-radius: 10px;
            white-space: pre-wrap;
        }

        @media (max-width: 600px) {
            body, .container {
                padding: 10px;
            }
        }
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
            try:
                headers = {
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}]
                }
                res = requests.post(DEEPSEEK_API_URL, headers=headers, try:
    data = res.json()
    if res.status_code == 200 and 'choices' in data:
        response = data['choices'][0]['message']['content']
    else:
        response = f"API Error: {data.get('error', data)}"
except Exception as e:
    response = f"Exception: {str(e)}"
            except Exception as e:
                response = f"Error: {str(e)}"

    return render_template_string(HTML, prompt=prompt, response=response)

if __name__ == "__main__":
    app.run(debug=True)