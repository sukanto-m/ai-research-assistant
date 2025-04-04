from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

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
    try:
        messages = query.messages  # Make sure this line is at the top of the function
        print("DEBUG messages:", messages)  # Optional: log the incoming messages

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        answer = response.choices[0].message.content

        return {"answer": answer}

    except Exception as e:
        print("Error occurred:", e)
        return {"answer": "An error occurred while processing your question."}


