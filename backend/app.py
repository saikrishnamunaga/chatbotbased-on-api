"""
Main Flask application for Rekuu AI Chatbot
Handles all API routes and server configuration
"""

import os
import io
import base64
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Import modules
from database import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    create_chat_session, get_chat_sessions, get_chat_session, delete_chat_session,
    save_message, get_chat_history, get_all_user_chats, update_chat_title, get_first_message
)
from auth import hash_password, verify_password, set_user_session, logout_user, login_required, get_current_user
from chatbot import get_ai_response, get_ai_response_with_image, get_ai_response_with_file
from file_handler import process_file, allowed_file, get_file_extension
from image_handler import allowed_image, process_image_for_vision

# Load environment variables
load_dotenv()

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app with explicit template folder
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'rekuu-secret-key-change-in-production')

# Enable CORS
CORS(app)

# Configure upload folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'uploads')
IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
FILES_FOLDER = os.path.join(UPLOAD_FOLDER, 'files')

# Create directories if they don't exist
os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(FILES_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
init_db()


# ==================== HTML Routes ====================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/register')
def register_page():
    """Registration page"""
    return render_template('register.html')


@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')


@app.route('/chat')
@login_required
def chat_page():
    """Chat dashboard page"""
    user_id = get_current_user()
    user = get_user_by_id(user_id)
    sessions = get_chat_sessions(user_id)
    return render_template('chat.html', user=user, sessions=sessions)


# ==================== API Routes ====================

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    # Validate input
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    # Validation checks
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    # Check if user already exists
    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # Create user
    password_hash = hash_password(password)
    user_id = create_user(name, email, password_hash)
    
    if user_id:
        return jsonify({'success': True, 'message': 'Registration successful! Please log in.'}), 201
    else:
        return jsonify({'success': False, 'message': 'Registration failed. Please try again.'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    # Get user from database
    user = get_user_by_email(email)
    
    if not user or not verify_password(user['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Set session
    set_user_session(user['id'], user['name'])
    
    return jsonify({
        'success': True, 
        'message': 'Login successful!',
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}
    }), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    user_id = get_current_user()
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return jsonify({'authenticated': True, 'user': user}), 200
    return jsonify({'authenticated': False}), 401


# ==================== Chat API Routes ====================

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Chat endpoint for text messages"""
    user_id = get_current_user()
    data = request.get_json()
    
    message = data.get('message', '').strip()
    session_id = data.get('session_id')
    
    if not message:
        return jsonify({'success': False, 'message': 'Message cannot be empty'}), 400
    
    # Create new session if not provided
    if not session_id:
        session_id = create_chat_session(user_id)
    
    # Save user message
    save_message(session_id, user_id, 'user', message, 'text')
    
    # Get chat history for context
    history = get_chat_history(session_id, user_id)
    
    # If this is the first message (only 1 message = user message), set the chat title
    if len(history) == 1:
        # Get first 5-7 words as title
        words = message.split()
        if len(words) <= 5:
            title = message
        else:
            title = ' '.join(words[:5]) + '...'
        update_chat_title(session_id, user_id, title)
    
    # Prepare messages for AI
    messages = []
    for msg in history:
        messages.append({
            'role': msg['role'],
            'content': msg['content']
        })
    
    # Get AI response
    try:
        ai_response = get_ai_response(messages)
    except Exception as e:
        return jsonify({'success': False, 'message': f'AI Error: {str(e)}'}), 500
    
    # Save AI response
    save_message(session_id, user_id, 'assistant', ai_response, 'text')
    
    return jsonify({
        'success': True,
        'response': ai_response,
        'session_id': session_id
    }), 200


@app.route('/api/chat-history', methods=['GET'])
@login_required
def chat_history():
    """Get chat history for a session"""
    user_id = get_current_user()
    session_id = request.args.get('session_id', type=int)
    
    if not session_id:
        # Get all sessions
        sessions = get_all_user_chats(user_id)
        return jsonify({'success': True, 'sessions': [dict(s) for s in sessions]}), 200
    
    # Get specific session
    session = get_chat_session(session_id, user_id)
    if not session:
        return jsonify({'success': False, 'message': 'Session not found'}), 404
    
    # Get messages
    messages = get_chat_history(session_id, user_id)
    
    return jsonify({
        'success': True,
        'session': dict(session),
        'messages': [dict(m) for m in messages]
    }), 200


@app.route('/api/new-chat', methods=['POST'])
@login_required
def new_chat():
    """Create a new chat session"""
    user_id = get_current_user()
    session_id = create_chat_session(user_id)
    return jsonify({'success': True, 'session_id': session_id}), 201


@app.route('/api/delete-chat', methods=['POST'])
@login_required
def delete_chat():
    """Delete a chat session"""
    user_id = get_current_user()
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'success': False, 'message': 'Session ID required'}), 400
    
    delete_chat_session(session_id, user_id)
    return jsonify({'success': True, 'message': 'Chat deleted'}), 200


# ==================== Image Upload API ====================

@app.route('/api/upload-image', methods=['POST'])
@login_required
def upload_image():
    """Handle image upload and analysis"""
    user_id = get_current_user()
    
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file provided'}), 400
    
    file = request.files['image']
    prompt = request.form.get('prompt', 'Describe this image in detail.').strip()
    session_id = request.form.get('session_id', type=int)
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_image(file.filename):
        return jsonify({'success': False, 'message': 'Invalid image format. Use PNG, JPG, or JPEG.'}), 400
    
    # Read file
    file_bytes = file.read()
    
    # Create new session if not provided
    if not session_id:
        session_id = create_chat_session(user_id)
    
    # Save user message with image indicator
    save_message(session_id, user_id, 'user', f'[Image: {file.filename}] {prompt}', 'image')
    
    try:
        # Process image for vision
        image_base64 = process_image_for_vision(file_bytes)
        
        # Get AI response with image
        ai_response = get_ai_response_with_image(image_base64, prompt)
        
    except Exception as e:
        ai_response = f"I apologize, but I encountered an error processing your image: {str(e)}"
    
    # Save AI response
    save_message(session_id, user_id, 'assistant', ai_response, 'text')
    
    return jsonify({
        'success': True,
        'response': ai_response,
        'session_id': session_id
    }), 200


# ==================== File Upload API ====================

@app.route('/api/upload-file', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload and analysis"""
    user_id = get_current_user()
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    prompt = request.form.get('prompt', 'Summarize this file and provide key insights.').strip()
    session_id = request.form.get('session_id', type=int)
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file format. Use PDF, TXT, DOCX, or CSV.'}), 400
    
    # Read file
    file_bytes = file.read()
    
    # Create new session if not provided
    if not session_id:
        session_id = create_chat_session(user_id)
    
    # Save user message with file indicator
    save_message(session_id, user_id, 'user', f'[File: {file.filename}] {prompt}', 'file')
    
    try:
        # Process file
        file_content, file_type = process_file(file_bytes, file.filename)
        
        if not file_content:
            return jsonify({'success': False, 'message': 'Could not extract text from file'}), 400
        
        # Get AI response with file
        ai_response = get_ai_response_with_file(file_content, file_type, prompt)
        
    except Exception as e:
        ai_response = f"I apologize, but I encountered an error processing your file: {str(e)}"
    
    # Save AI response
    save_message(session_id, user_id, 'assistant', ai_response, 'text')
    
    return jsonify({
        'success': True,
        'response': ai_response,
        'session_id': session_id
    }), 200



# ==================== Static Files ====================

@app.route('/style.css')
def serve_css():
    """Serve CSS file"""
    frontend_dir = os.path.join(os.path.dirname(BASE_DIR), 'frontend')
    return send_from_directory(frontend_dir, 'style.css')

@app.route('/script.js')
def serve_js():
    """Serve JS file"""
    frontend_dir = os.path.join(os.path.dirname(BASE_DIR), 'frontend')
    return send_from_directory(frontend_dir, 'script.js')


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'success': False, 'message': 'Page not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({'success': False, 'message': 'Internal server error'}), 500


# ==================== Main===================

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Rekuu AI Chatbot...")
    print("=" * 50)
    print(f"Server running at: http://127.0.0.1:5000")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
