# 🧠 AI Research Assistant

A full-stack AI-native application that lets you ask natural language questions and get helpful answers powered by OpenAI GPT-4o. Built with:

- 🐍 FastAPI (backend)
- ⚛️ React + Tailwind CSS (frontend)
- 🤖 GPT-4o via OpenAI API
- 💬 Memory-powered multi-turn conversations

## 🔧 Local Setup

### Backend (FastAPI + OpenAI)

```bash
cd backend
conda activate ai-research-assistant
uvicorn main:app --reload
