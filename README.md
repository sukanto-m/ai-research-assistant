# 🧠 AI Research Assistant

A full-stack AI-native application that lets you ask natural language questions and get helpful answers powered by OpenAI GPT-4o.

Built with:
- 🐍 FastAPI (backend)
- ⚛️ React + Tailwind CSS (frontend)
- 🤖 GPT-4o via OpenAI API
- 💬 Memory-powered multi-turn conversations

---

## ✨ Features

- 📤 Upload documents: `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.csv`, `.txt`, `.md`, `.html`
- 🧠 Ask follow-up questions in a natural conversation flow
- 📊 Auto-generate charts (bar, line, pie, radar, doughnut) from tabular data
- 🧾 See structured Markdown-formatted answers
- 📄 Export chat history and charts as a downloadable PDF
- 🛡️ **Privacy-first**: No data stored, files are deleted after use

---

## 🔐 Privacy Commitment

This app is designed with privacy in mind:

- All uploaded documents are processed locally
- No content is stored after the analysis is complete
- Documents are **auto-deleted** immediately after vector embedding
- Assistant responses are generated in-memory using OpenAI’s API

---

## 🚀 Getting Started

### 🔧 Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
