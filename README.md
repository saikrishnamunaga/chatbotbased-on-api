# Rekuu AI Chatbot

A modern AI chatbot web application built with Flask and Groq API. Rekuu supports text chat, image understanding, and file analysis powered by Llama 3 and Mixtral models.

![Rekuu AI](https://img.shields.io/badge/Rekuu-AI%20Chatbot-purple)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 💬 **Smart Chat** - Natural conversations with context-aware AI responses
- 🖼️ **Image Analysis** - Upload images and get intelligent descriptions using vision models
- 📄 **File Analysis** - Analyze PDFs, TXT, DOCX, and CSV files
- 🔐 **User Authentication** - Secure registration and login system
- 💾 **Chat History** - Save and load previous conversations
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 🎨 **Modern UI** - Beautiful gradient design with glassmorphism effects

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Groq API Key ([Get it here](https://console.groq.com/))

### Installation

1. **Clone or download this repository**

2. **Navigate to the project directory**
   ```bash
   cd rekuu-ai-chatbot
   ```

3. **Create a virtual environment (recommended)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**

   Open the `.env` file and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

   To get a free Groq API key:
   1. Visit [console.groq.com](https://console.groq.com/)
   2. Sign up for an account
   3. Navigate to API Keys
   4. Create a new API key
   5. Copy and paste it into the `.env` file

6. **Run the application**
   ```bash
   cd backend
   python app.py
   ```

7. **Open in browser**
   Navigate to: `http://127.0.0.1:5000`

## 📖 Usage

### User Registration
1. Click "Get Started" on the landing page
2. Fill in your name, email, and password
3. Click "Create Account"
4. Login with your credentials

### Chat Features
- **Text Chat**: Type your message and press Enter or click Send
- **Image Upload**: Click the image icon to upload PNG/JPG/JPEG images
- **File Analysis**: Click the file icon to upload PDF, TXT, DOCX, or CSV files

### Quick Actions
- Start new conversations with "New Chat"
- View previous chats in the sidebar
- Delete old conversations

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register` | POST | Register new user |
| `/api/login` | POST | User login |
| `/api/logout` | POST | User logout |
| `/api/chat` | POST | Send text message |
| `/api/upload-image` | POST | Upload and analyze image |
| `/api/upload-file` | POST | Upload and analyze file |
| `/api/chat-history` | GET | Get chat history |
| `/api/new-chat` | POST | Create new chat session |
| `/api/delete-chat` | POST | Delete chat session |

## 📁 Project Structure

```
rekuu-ai-chatbot/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── auth.py             # Authentication utilities
│   ├── database.py         # SQLite database functions
│   ├── chatbot.py          # Groq API integration
│   ├── file_handler.py      # File processing
│   └── image_handler.py    # Image processing
├── frontend/
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── chat.html           # Chat interface
│   ├── style.css           # Styling
│   └── script.js           # Frontend JavaScript
├── uploads/                # Uploaded files
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key (required) |
| `FLASK_SECRET_KEY` | Secret key for sessions (optional) |

### Supported Models

- `llama3-70b-8192` (default) - Powerful general-purpose model
- `llama3-8b-8192` - Faster, lighter model
- `llama-3.2-11b-vision-preview` - For image analysis

## 🤖 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python 3.8+, Flask 3.0
- **Database**: SQLite
- **AI**: Groq API (Llama 3, Mixtral)
- **Authentication**: Werkzeug password hashing

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for providing the AI API
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [PyPDF2](https://github.com/pypdf2/PyPDF2) for PDF processing
- [python-docx](https://python-docx.readthedocs.io/) for DOCX processing

## ⚠️ Important Notes

1. **API Key Required**: You must have a valid Groq API key to use the chatbot
2. **Rate Limits**: Groq has rate limits depending on your plan
3. **File Size**: Maximum upload size is 16MB
4. **Supported Formats**: 
   - Images: PNG, JPG, JPEG
   - Files: PDF, TXT, DOCX, CSV

## 🔒 Security

- Passwords are hashed using SHA-256
- Session-based authentication
- Input validation on all forms
- CORS enabled for API security

---

<p align="center">Made with ❤️ by Rekuu AI</p>

