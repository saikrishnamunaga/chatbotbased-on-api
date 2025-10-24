# AI Chatbot using Google Gemini API 🤖

A simple AI-powered chatbot built with **Google Generative AI (Gemini models)** in Python. Interact with the bot in real-time through your terminal.

---

## 🌟 Features

- Uses Google Gemini models for natural language generation.
- Supports multiple chat models:
  - `models/gemini-flash-latest`
  - `models/gemini-2.5-flash`
  - `models/gemini-2.5-pro`
- Configurable API key via `.env` file.
- Terminal-based interactive chat interface.
- Graceful error handling and exit via `exit` or `quit`.

---

## 🛠️ Requirements

- Python 3.10+
- [google-generativeai](https://pypi.org/project/google-generativeai/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

Install dependencies:

```bash
pip install google-generativeai python-dotenv
