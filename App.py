from flask import Flask, render_template_string, request, jsonify
import pyttsx3
import random
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize TTS engine (using default driver)
engine = pyttsx3.init()

# Set TTS properties (optional)
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

# Basic chatbot responses
responses = {
    "hello": ["Hi!", "Hello!", "Hey there!"],
    "how are you": ["I'm doing great, thank you!", "I'm just a bot, but I'm doing well!"],
    "bye": ["Goodbye!", "See you later!"],
}

# Function to convert text to speech (TTS)
def speak(text):
    # Save the speech output as an mp3 file in the static folder
    engine.save_to_file(text, 'static/response.mp3')
    engine.runAndWait()

@app.route('/')
def home():
    return render_template_string(html_template)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message').lower()
    response = responses.get(user_input, ["Sorry, I didn't understand that."])
    
    # Trigger TTS for the response
    speak(response[0])  # Respond with the first possible answer (random or predefined)
    
    return jsonify({'response': response[0]})

# HTML, CSS, and JavaScript embedded in the Python script
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot with TTS</title>
    <style>
        /* General page styles */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f7f6;
        }
        
        /* Chat container */
        .chat-container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        /* Heading */
        h1 {
            text-align: center;
            font-size: 2em;
            color: #333;
        }

        /* Chat box */
        .chat-box {
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f1f1f1;
            border-radius: 10px;
        }

        /* Input container */
        .input-container {
            display: flex;
            justify-content: space-between;
        }

        /* Input field */
        #user-input {
            width: 80%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        /* Send button */
        #send-btn {
            width: 15%;
            padding: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        /* Hover effect for button */
        #send-btn:hover {
            background-color: #45a049;
        }

        /* Message styles */
        .message {
            margin: 10px;
            padding: 10px;
            border-radius: 5px;
        }

        .message.user {
            background-color: #e1f5fe;
            text-align: left;
        }

        .message.bot {
            background-color: #f1f1f1;
            text-align: right;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <h1>Chat with Bot!</h1>
        <div class="chat-box" id="chat-box"></div>
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Type a message" />
            <button id="send-btn">Send</button>
        </div>
    </div>
    <script>
        const sendBtn = document.getElementById('send-btn');
        const userInput = document.getElementById('user-input');
        const chatBox = document.getElementById('chat-box');

        sendBtn.addEventListener('click', function() {
            const message = userInput.value;
            if (!message.trim()) return;

            // Display user message in chat box
            const userMessage = document.createElement('div');
            userMessage.classList.add('message', 'user');
            userMessage.textContent = message;
            chatBox.appendChild(userMessage);

            // Clear input field
            userInput.value = '';

            // Send message to Flask backend
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                const botMessage = document.createElement('div');
                botMessage.classList.add('message', 'bot');
                botMessage.textContent = data.response;
                chatBox.appendChild(botMessage);

                // Play the TTS response
                const audio = new Audio('/static/response.mp3');
                audio.play();
            });
        });
    </script>
</body>
</html>
"""

# Run the app
if __name__ == '__main__':
    app.run(debug=True)