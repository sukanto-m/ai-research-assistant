from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

# This will be our global in-memory store for now
vector_store = None

def load_and_embed_pdf(file_path: str):
    global vector_store

    # Step 1: Load PDF
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    # Step 2: Chunk the text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)

    # Step 3: Embed and create FAISS index
    vector_store = FAISS.from_documents(chunks, embedding_model)
    print(f"✅ Document indexed with {len(chunks)} chunks.")

def get_relevant_chunks(query: str, k: int = 3) -> str:
    if vector_store is None:
        return "⚠️ No document uploaded yet."

    docs = vector_store.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in docs])
