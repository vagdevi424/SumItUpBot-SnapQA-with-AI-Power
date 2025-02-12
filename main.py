import os
import shutil
import openai
import pdfplumber
import docx2txt
import pandas as pd
import pytesseract
import faiss
import numpy as np
import re
import docx
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FastAPI App
app = FastAPI()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY in the .env file or environment variables.")

client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Correct OpenAI client setup

# Directory for file uploads
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load a lightweight embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# FAISS Index for storing document embeddings
dimension = 384  # Embedding size of MiniLM
faiss_index = faiss.IndexFlatL2(dimension)
document_chunks = []  # Stores text chunks corresponding to embeddings

# In-memory storage for uploaded document content
uploaded_files = {}

# ==============================
# File Processing Functions
# ==============================
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read()

def extract_text_from_excel(excel_path):
    df = pd.read_excel(excel_path)
    return df.to_string()

def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

def process_uploaded_file(file_path, file_type):
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == "docx":
        return extract_text_from_docx(file_path)
    elif file_type == "txt":
        return extract_text_from_txt(file_path)
    elif file_type == "xlsx":
        return extract_text_from_excel(file_path)
    elif file_type in ["png", "jpeg", "jpg"]:
        return extract_text_from_image(file_path)
    else:
        return "Unsupported file format"

# ==============================
# FAISS Indexing & Retrieval
# ==============================
def index_document(text):
    """Splits document into sentences and stores them in FAISS."""
    global document_chunks
    document_chunks = text.split(". ")

    embeddings = embedding_model.encode(document_chunks, convert_to_numpy=True)
    faiss_index.add(embeddings)

def retrieve_relevant_text(query, top_k=3):
    """Retrieves the most relevant document sections using FAISS."""
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = faiss_index.search(query_embedding, top_k)

    relevant_text = " ".join([document_chunks[i] for i in indices[0] if i < len(document_chunks)])
    return relevant_text

# ==============================
# FastAPI Endpoints
# ==============================
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Handles file uploads, extracts text, stores it in FAISS, and generates a cleaned summary using GPT-4o-mini."""
    file_location = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_type = file.filename.split(".")[-1].lower()
    extracted_text = process_uploaded_file(file_location, file_type)

    if extracted_text == "Unsupported file format":
        return {"error": "Unsupported file format"}

    uploaded_files["latest"] = extracted_text
    index_document(extracted_text)

    # Generate Summary using GPT-4o-mini
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role": "user", "content": f"Summarize this document concisely:\n\n{extracted_text}"}]
    # )
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an AI assistant that generates professional, concise summaries from documents. The summary should be structured in complete sentences, avoiding unnecessary details and repetitive content."},
        {"role": "user", "content": f"Summarize the key points from this document in clear, structured sentences:\n\n{extracted_text}"},
    ]
)


    raw_summary = response.choices[0].message.content.strip()

    # Clean the summary text
    clean_summary = re.sub(r'[\*\[\]_\n]', ' ', raw_summary)  # Remove markdown symbols and newlines
    clean_summary = re.sub(r'\s+', ' ', clean_summary).strip()  # Remove extra spaces

    return {
        "filename": file.filename,
        "summary": clean_summary
    }

@app.post("/qa/")
async def ask_question(question: str = Form(...)):
    """Retrieves the most relevant section from FAISS and uses GPT-4o-mini to answer the question."""
    if "latest" not in uploaded_files or not uploaded_files["latest"]:
        raise HTTPException(status_code=400, detail="No document uploaded. Please upload a file first.")

    relevant_text = retrieve_relevant_text(question)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant that answers questions based on document content."},
            {"role": "user", "content": f"Context:\n{relevant_text}\n\nQuestion: {question}\nAnswer:"}
        ]
    )

    answer = response.choices[0].message.content.strip()

    return {"answer": answer}

# ==============================
# Run FastAPI Server
# ==============================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
