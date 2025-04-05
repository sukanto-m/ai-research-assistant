from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
import os
import shutil
import json

from utils.rag_utils import load_and_embed_file, get_relevant_chunks
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]


def load_system_prompt():
    with open("utils/chart_prompt.prompt", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if background_tasks:
        background_tasks.add_task(os.remove, file_path)

    try:
        load_and_embed_file(file_path)
        return {"message": "✅ File uploaded and processed successfully."}
    except Exception as e:
        return {"message": f"❌ Failed to process file: {str(e)}"}


@app.post("/ask")
async def ask(request: ChatRequest):
    client = OpenAI()
    system_prompt = load_system_prompt()

    messages = [{"role": "system", "content": system_prompt}] + [m.model_dump() for m in request.messages]

    user_query = request.messages[-1].content
    context = get_relevant_chunks(user_query)
    if context and "⚠️" not in context:
        messages.insert(1, {
            "role": "user",
            "content": f"Relevant document info:\n{context}"
        })

    # Debug log (optional)
    print("\n==== Prompt sent to GPT ====")
    print(json.dumps(messages, indent=2))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3
    )

    return {"answer": response.choices[0].message.content}
