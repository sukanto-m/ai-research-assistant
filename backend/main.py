from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import shutil
from dotenv import load_dotenv
from rag_utils import load_and_embed_file, get_relevant_chunks
import json 

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class Query(BaseModel):
    messages: list[Message]

def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_location = f"backend/uploads/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        load_and_embed_file(file_location)
    except ValueError as e:
        return {"error": str(e)}

    # Flag if it's a tabular file (for special system prompt)
    is_tabular = file.filename.endswith((".csv", ".xlsx"))
    with open("backend/tabular_mode.txt", "w") as f:
        f.write("true" if is_tabular else "false")

    background_tasks.add_task(delete_file, file_location)

    return {"message": f"{file.filename} uploaded and processed successfully."}

@app.post("/ask")
async def ask_question(query: Query):
    messages = [m.dict() if isinstance(m, BaseModel) else m for m in query.messages]

    latest_question = next((m["content"] for m in reversed(messages) if m["role"] == "user"), None)

    if latest_question:
        rag_context = get_relevant_chunks(latest_question)

        # Check if a tabular file was uploaded recently
        try:
            with open("backend/tabular_mode.txt", "r") as f:
                tabular_mode = f.read().strip().lower() == "true"
        except FileNotFoundError:
            tabular_mode = False

        system_prompt = (
    "You are a data analysis assistant. When asked to analyze tabular data, respond with clear summaries. "
   "If a chart would help, add a chart block like this:\n\n"
"chart: {\n"
"  \"type\": \"line\",  // or bar, pie, doughnut, radar\n"
"  \"labels\": [...],\n"
"  \"datasets\": [...][{\"label\": \"...\", \"data\": [...], \"backgroundColor\": \"...\"]\n"
    "}\n"
    "Only include the chart: block if it's directly relevant to the user's question."
    if tabular_mode
    else "You are a helpful research assistant."
)


        insert_index = 1 if messages[0]["role"] == "system" else 0
        messages.insert(insert_index, {
            "role": "system",
            "content": f"{system_prompt}\n\nUse the following context:\n\n{rag_context}"
        })

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    
    return {"answer": response.choices[0].message.content}
