import os 
import random 
import time 
import wikipedia 
import socketio 
from fastapi import FastAPI, Request, Form 
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse from fastapi.staticfiles import StaticFiles from fastapi.templating import Jinja2Templates from supabase import create_client from gtts import gTTS from googleapiclient.discovery import build from threading import Thread

----- Setup Supabase -----

SUPABASE_URL = os.environ.get("SUPABASE_URL") SUPABASE_KEY = os.environ.get("SUPABASE_KEY") supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

----- Socket.IO + FastAPI -----

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*") app = FastAPI() sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

----- Static & Templates -----

app.mount("/static", StaticFiles(directory="static"), name="static") templates = Jinja2Templates(directory="templates")

----- Chatbot Logic -----

english_responses = { "hello": ["Hello there! How can I assist you today?", "Hi! Need anything?", "Hey! I'm here to help."], "how are you": ["Doing great! How about you?", "All systems go!"], "bye": ["Catch you later!", "Goodbye! Stay awesome!"], }

def detect_query_type(text): text = text.lower().strip() if "who is" in text: return "who" elif "what is" in text: return "what" elif "where is" in text: return "where" return "chat"

def extract_topic(text): for keyword in ["play", "show me", "turn on", "video of"]: if keyword in text: return text.split(keyword, 1)[1].strip() return text.strip()

def search_wikipedia(query, sentences=2): try: summary = wikipedia.summary(query, sentences=sentences) return f"According to Wikipedia: {summary}" except wikipedia.DisambiguationError as e: return f"Too many results. Suggestions: {', '.join(e.options[:3])}" except wikipedia.PageError: return "Couldn't find anything." except Exception as e: return f"Error: {str(e)}"

def search_youtube_video(query): try: api_key = os.environ.get("YOUTUBE_API_KEY") youtube = build("youtube", "v3", developerKey=api_key) request = youtube.search().list(part="snippet", q=query, type="video", maxResults=1) response = request.execute() items = response.get("items") if items: vid = items[0]["id"]["videoId"] title = items[0]["snippet"]["title"] return f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{vid}" frameborder="0" allowfullscreen></iframe><br>{title}' return "No video found." except Exception as e: return f"Error: {str(e)}"

def get_chatbot_response(user_input, name="User"): user_input = user_input.lower() for key, replies in english_responses.items(): if key in user_input: return f"{name}, {random.choice(replies)}" return f"{name}, I didn't get that."

def cleanup_audio(filename): time.sleep(10) if os.path.exists(filename): os.remove(filename)

----- Socket Events -----

@sio.event async def connect(sid, environ): print(f"[+] Connected: {sid}") await sio.emit('bot_message', "Connected to Sanji AI!", to=sid)

@sio.event async def disconnect(sid): print(f"[-] Disconnected: {sid}")

@sio.event async def user_message(sid, data): name = data.get("name", "User") message = data.get("message", "") print(f"[{name}] {message}") if any(k in message.lower() for k in ["play", "show me", "video of", "turn on"]): topic = extract_topic(message) response = search_youtube_video(topic) else: intent = detect_query_type(message) if intent in ["who", "what", "where"]: topic = extract_topic(message) response = search_wikipedia(topic) else: response = get_chatbot_response(message, name) await sio.emit('bot_message', response, to=sid)

----- Text-to-Speech Endpoint -----

@app.get("/speak") async def speak(text: str): if not text: return JSONResponse({"error": "No text provided."}, status_code=400) filename = f"speech_{random.randint(1000, 9999)}.mp3" tts = gTTS(text) tts.save(filename) Thread(target=cleanup_audio, args=(filename,)).start() return FileResponse(filename, media_type="audio/mpeg")

----- User Info Endpoints -----

@app.post("/update_username") async def update_username(request: Request): session = request.session if "token" not in session: return JSONResponse({"error": "Not authenticated"}, status_code=401) data = await request.json() username = data.get("username", "").strip() if not username: return JSONResponse({"error": "Username cannot be empty."}, status_code=400) email = session.get("email") supabase.table("user_memories").insert({ "user_mail": email, "memory_type": "setting", "memory_key": "preferred_name", "memory_value": username }).execute() session["name"] = username return {"message": "Username updated successfully!"}

@app.get("/get_user_info") async def get_user_info(request: Request): session = request.session if "token" not in session: return JSONResponse({"error": "Not authenticated"}, status_code=401) return {"email": session.get("email"), "name": session.get("name", "User")}

----- GUI -----

@app.get("/chat") async def chat_ui(request: Request): theme_gradient = "radial-gradient(circle at top, #0E0307 0%, #1b0b2e 100%)"  # Placeholder email = request.cookies.get("email", "guest") return templates.TemplateResponse("chat.html", {"request": request, "theme_gradient": theme_gradient, "email": email})

@app.get("/settings") async def settings_ui(request: Request): theme_gradient = "radial-gradient(circle at top, #0E0307 0%, #1b0b2e 100%)"  # Placeholder email = request.cookies.get("email", "guest") return templates.TemplateResponse("settings.html", {"request": request, "theme_gradient": theme_gradient, "email": email})

@app.get("/") async def index(): return RedirectResponse(url="/chat")

Run with: uvicorn main:sio_app --reload

