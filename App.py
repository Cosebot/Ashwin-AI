from flask import Flask, render_template_string, request, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

app = Flask(__name__)

# Load GPT-2
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)
model.eval()

# HTML UI Template
index_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Sanji AI - GPT-2 Playground</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            background: linear-gradient(135deg, #1b0b2e, #6E33B1);
            color: #fff;
            font-family: 'SF Pro Display', sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        h1 {
            margin-top: 20px;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            max-width: 600px;
            width: 90%;
            box-shadow: 0 0 20px #6E33B1;
        }
        textarea {
            width: 100%;
            height: 120px;
            border-radius: 10px;
            border: none;
            padding: 10px;
            font-size: 16px;
            background: rgba(255,255,255,0.2);
            color: #fff;
            margin-bottom: 15px;
            resize: none;
        }
        button {
            background: #6E33B1;
            color: #fff;
            border: none;
            border-radius: 30px;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #8f45f4;
        }
        .response {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h1>Sanji AI - GPT-2 Playground</h1>
    <div class="container">
        <textarea id="prompt" placeholder="Enter your prompt here..."></textarea>
        <button onclick="generateText()">Generate</button>
        <div id="response" class="response"></div>
    </div>
    <script>
        async function generateText() {
            const prompt = document.getElementById("prompt").value;
            const responseDiv = document.getElementById("response");
            responseDiv.innerText = "Generating...";
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: prompt})
            });
            const data = await response.json();
            responseDiv.innerText = data.response;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(index_html)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(
            inputs, 
            max_length=150, 
            num_return_sequences=1, 
            temperature=0.7,
            top_k=50,
            pad_token_id=tokenizer.eos_token_id
        )
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({"response": text})

if __name__ == "__main__":
    app.run(debug=True)