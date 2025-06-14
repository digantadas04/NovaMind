from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import requests
import os
import PyPDF2
import docx
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# Config
app.secret_key = 'your-secret-key-here-change-this-in-production'
OLLAMA_URL = "http://localhost:11434/api/generate"
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory conversation storage (use database in production)
conversations = {}

def get_session_id():
    """Get or create a unique session ID for the user"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_conversation_context(session_id, max_messages=10):
    """Get recent conversation history for context"""
    if session_id not in conversations:
        conversations[session_id] = []
    
    # Return last max_messages messages
    recent_messages = conversations[session_id][-max_messages:]
    context = ""
    
    for msg in recent_messages:
        if msg['role'] == 'user':
            context += f"User: {msg['content']}\n"
        else:
            context += f"NovaMind: {msg['content']}\n"
    
    return context

def add_to_conversation(session_id, role, content):
    """Add a message to the conversation history"""
    if session_id not in conversations:
        conversations[session_id] = []
    
    conversations[session_id].append({
        'role': role,
        'content': content,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 50 messages to prevent memory overflow
    if len(conversations[session_id]) > 50:
        conversations[session_id] = conversations[session_id][-50:]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    session_id = get_session_id()
    
    # Get conversation context
    context = get_conversation_context(session_id)
    
    # Build prompt with context
    if context:
        prompt = f"""You are NovaMind, an intelligent and friendly AI assistant. Here's our conversation history:

{context}

Continue the conversation naturally, referring to previous messages when relevant.

User: {user_msg}
NovaMind:"""
    else:
        prompt = f"You are NovaMind, an intelligent and friendly AI assistant.\nUser: {user_msg}\nNovaMind:"
    
    payload = {
        "model": "gemma3:4b",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        data = response.json()
        reply = data.get("response", "Sorry, I couldn't generate a response.")
        reply = reply.strip()
        
        # Add both user message and AI response to conversation history
        add_to_conversation(session_id, 'user', user_msg)
        add_to_conversation(session_id, 'assistant', reply)
        
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

@app.route("/clear-conversation", methods=["POST"])
def clear_conversation():
    """Clear the conversation history for the current session"""
    session_id = get_session_id()
    if session_id in conversations:
        conversations[session_id] = []
    return jsonify({"status": "success", "message": "Conversation cleared"})

@app.route("/get-conversation-stats", methods=["GET"])
def get_conversation_stats():
    """Get basic stats about the current conversation"""
    session_id = get_session_id()
    if session_id not in conversations:
        return jsonify({"message_count": 0, "session_id": session_id})
    
    message_count = len(conversations[session_id])
    return jsonify({"message_count": message_count, "session_id": session_id})

@app.route("/summarize", methods=["POST"])
def summarize():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
    file.save(filepath)

    ext = file.filename.rsplit(".", 1)[-1].lower()
    text = ""

    try:
        if ext == "pdf":
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = " ".join(page.extract_text() or "" for page in reader.pages)
        elif ext == "txt":
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == "docx":
            doc = docx.Document(filepath)
            text = "\n".join(para.text for para in doc.paragraphs)
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        # Generate summary with context awareness
        session_id = get_session_id()
        context = get_conversation_context(session_id, max_messages=5)
        
        if context:
            prompt = f"""You are NovaMind. Here's our recent conversation:

{context}

Now, please summarize this document (keeping our conversation context in mind if relevant):
{text[:4000]}"""
        else:
            prompt = f"You are NovaMind. Summarize this document:\n{text[:4000]}"
        
        payload = {
            "model": "gemma3:4b",
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload)
        summary = response.json().get("response", "Failed to summarize.")
        summary = summary.strip()
        
        # Add file summary to conversation history
        add_to_conversation(session_id, 'user', f"[Uploaded file: {file.filename}]")
        add_to_conversation(session_id, 'assistant', f"File Summary: {summary}")
        
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == "__main__":
    app.run(debug=True)