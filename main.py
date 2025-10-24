import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found or not set.")
    exit()

genai.configure(api_key=api_key)


model = genai.GenerativeModel('models/gemini-flash-latest')
chat = model.start_chat(history=[])

def main():
    print("Welcome to the AI Chatbot! Type 'exit' or 'quit' to end the conversation.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: Goodbye!")
            break
        try:
            response = chat.send_message(user_input)
            print(f"Chatbot: {response.text}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
