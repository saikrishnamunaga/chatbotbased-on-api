"""
Chatbot module for Rekuu AI Chatbot
Handles Groq API integration for AI responses
"""

import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Groq API key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# System prompt for Rekuu AI
SYSTEM_PROMPT = """You are Rekuu, a smart and friendly AI assistant that helps users with programming, learning, productivity, research, and daily tasks.

Your characteristics:
- Helpful, knowledgeable, and patient
- Provide clear and detailed explanations
- Break down complex topics into understandable parts
- When answering code questions, provide working examples
- Be concise but thorough
- If you don't know something, admit it honestly
- Always maintain a friendly and professional tone"""


def get_groq_client():
    """Get Groq client instance"""
    if not GROQ_API_KEY or GROQ_API_KEY == 'your_api_key_here':
        raise ValueError("Please set your Groq API key in the .env file")
    return Groq(api_key=GROQ_API_KEY)


def get_ai_response(messages, model="llama-3.3-70b-versatile"):
    """
    Get AI response from Groq API
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Groq model to use (default: llama-3.3-70b-versatile)
    
    Returns:
        AI response as string
    """
    try:
        client = get_groq_client()
        
        # Add system prompt to messages
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Add conversation history
        for msg in messages:
            full_messages.append(msg)
        
        # Make API call
        chat_completion = client.chat.completions.create(
            messages=full_messages,
            model=model,
            temperature=0.7,
            max_tokens=4096,
            top_p=0.9,
            stream=False
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please check your API key and try again."


def get_ai_response_with_image(image_data, prompt, model="llama-3.2-11b-vision-preview"):
    """
    Get AI response for image analysis using vision capabilities
    
    Args:
        image_data: Base64 encoded image data
        prompt: User's question about the image
        model: Groq model to use
    
    Returns:
        AI response as string
    """
    try:
        client = get_groq_client()
        
        # Create message with image
        messages = [
            {
                "role": "system", 
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ]
        
        # Make API call with vision model
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.2-11b-vision-preview",
            temperature=0.7,
            max_tokens=4096,
            top_p=0.9,
            stream=False
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, but I encountered an error analyzing the image: {str(e)}. Please try again with a different image."


def get_ai_response_with_file(file_content, file_type, prompt, model="llama-3.3-70b-versatile"):
    """
    Get AI response for file analysis
    
    Args:
        file_content: Extracted text from file
        file_type: Type of file (pdf, txt, docx, csv)
        prompt: User's question about the file
        model: Groq model to use
    
    Returns:
        AI response as string
    """
    try:
        client = get_groq_client()
        
        # Create context about the file
        file_context = f"The following content is from a {file_type.upper()} file:\n\n{file_content}"
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user", 
                "content": f"{file_context}\n\nUser's question: {prompt}"
            }
        ]
        
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0.7,
            max_tokens=4096,
            top_p=0.9,
            stream=False
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, but I encountered an error analyzing the file: {str(e)}. Please try again."

