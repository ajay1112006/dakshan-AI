# ⚡ Dakshan AI

An ultra-fast, interactive command-line assistant powered by Python.

---

## ✨ Features

- **⚡ Lightning-Fast Responses**: Real-time token streaming with Groq's high-speed inference.
- **🎨 Beautiful Terminal UI**: Powered by `rich` with syntax highlighting, markdown rendering, and clean panels.
- **🧠 Multi-Turn Memory**: Keeps conversation context across turns.
- **🔄 Dynamic Model Switching**: Switch easily between top models (`Llama 3.3 70B`, `DeepSeek R1 Distill 70B`, `Llama 3.1 8B`, `Mixtral 8x7B`, `Gemma 2 9B`).
- **⚙️ Interactive Commands**:
  - `/help`: Display list of commands.
  - `/model`: Switch or view LLM models.
  - `/system`: Update system instructions in real-time.
  - `/clear`: Clear conversation history and start fresh.
  - `/save`: Export the conversation to a Markdown file.
  - `/history`: Check total message count and turns.
  - `/exit` or `/quit`: Cleanly exit the chat.
- **🔑 Automatic Key Setup**: Enter your API key interactively on first run or configure via `.env`.

---

## 🚀 Quick Start

### 1. Configure Your API Key
Optionally copy `.env.example` to `.env` and paste your key:
```bash
copy .env.example .env
```
Open `.env` and replace `your_groq_api_key_here` with your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_key_here
```
*(If you skip this step, the chatbot will prompt you to enter and save it on your first run.)*

---

### 2. Run the Chatbot

You can launch it in **one command**:
```bash
.\run.bat
```

Or manually using the virtual environment:
```powershell
# Activate virtual environment (if not already activated)
.\.venv\Scripts\activate

# Run the chatbot
python chatbot.py
```

---

## 📦 Requirements

The project uses:
- `groq` (Official Groq Python SDK)
- `rich` (Terminal styling & markdown rendering)
- `python-dotenv` (Environment variable management)

To reinstall or update dependencies:
```bash
.\.venv\Scripts\pip install -r requirements.txt
```
