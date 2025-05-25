from flask import Flask, request, jsonify, render_template_string
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

app = Flask(__name__)

model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
chatbot = pipeline("text-generation", model=model, tokenizer=tokenizer)

HTML = """ 
<!-- your HTML stays unchanged, not repeating for brevity -->
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
        result = chatbot(prompt, max_length=100, pad_token_id=tokenizer.eos_token_id)
        response_text = result[0]['generated_text'].strip()
        # Remove the original prompt from the response if DialoGPT repeats it
        if response_text.lower().startswith(prompt.lower()):
            response_text = response_text[len(prompt):].strip()
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)