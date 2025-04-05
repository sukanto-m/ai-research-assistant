from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
from rag_utils import get_relevant_chunks, load_and_embed_pdf
from fastapi import UploadFile, File
import shutil

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # allow your React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role:str
    content:str

# Define request model
class Query(BaseModel):
    messages: list[Message]


# Define endpoint
@app.post("/ask")
async def ask_question(query: Query):
    messages = query.messages

    # 1. Extract the latest user message (the actual question)
    latest_question = [m.content for m in messages if m.role == "user"][-1]

    # 2. Use the question to get relevant RAG chunks
    rag_context = get_relevant_chunks(latest_question)

    # 3. Inject retrieved context right after system message
    messages.insert(1, {
        "role": "system",
        "content": f"Use the following context to help answer the question:\n\n{rag_context}"
    })

    # 4. Send to OpenAI
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages

    )

    answer = response.choices[0].message.content
    return {"answer": answer}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Save uploaded file to disk
    file_location = f"backend/uploads/{file.filename}"

    # Make sure the upload folder exists
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load and embed the uploaded file
    load_and_embed_pdf(file_location)

    return {"message": f"{file.filename} uploaded and indexed successfully."}

