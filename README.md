# NovaMind

NovaMind is a locally hosted AI-powered chatbot assistant built using **Python, Flask, and Ollama's Gemma3:4b LLM**. It offers real-time conversational capabilities with session-based memory and file summarization. The project features a responsive, modern web interface where users can interact with the AI, upload documents for summarization, and enjoy a polished chat experience entirely on their own machine.

---

## 🧠 Features

- 💬 Conversational AI powered by Ollama Gemma3:4b
- 📄 Summarize PDF, TXT, and DOCX files via file upload
- 🧩 Session-based conversation memory
- 🎨 Aesthetic UI with nickname personalization
- 🌙 Light/Dark mode toggle
- 🗑 Clear chat feature and message counter

---

## 🚀 Technologies Used

- **Backend:** Python, Flask, Flask-CORS
- **Frontend:** HTML, CSS, JavaScript
- **LLM Integration:** Ollama Gemma3:4b Model
- **File Processing:** PyPDF2 (PDF), python-docx (DOCX)
- **UI Design:** Custom modern CSS with responsive design

## 📂 Project Structure

│
├── app.py # Backend logic (Flask + Ollama integration)
├── templates/
│ └── index.html # Frontend chat interface
├── static/
│ └── style.css # Styling for UI
├── uploads/ # Temporary folder for uploaded files
├── README.md # Project documentation
├── requirements.txt # Python dependencies (to be generated)
└── .gitignore # Files to ignore (to be generated)

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed and running locally
- Download `gemma3:4b` model:
  ollama pull gemma3:4b
  
Install Required Python Packages
pip install flask flask-cors PyPDF2 python-docx requests
Run Ollama (if not already running)
ollama serve

Start the Flask Application
python app.py
Then, open your browser and visit http://localhost:5000/ to start chatting with NovaMind.

## 🔮 Future Scope
Add persistent memory using vector databases like ChromaDB

Integrate speech recognition and text-to-speech

Implement task management and system control features

Multi-modal capabilities and broader file format support

## 📜 License
For personal, educational, and non-commercial use only.

## 🙏 Acknowledgements
Ollama AI Platform

Google Gemma Model

Python, Flask, and Open Source Community
