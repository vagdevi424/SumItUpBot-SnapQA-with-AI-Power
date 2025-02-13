# SumItUpBot: SnapQ&A with AI Power

## Overview

SumItUpBot is an AI-powered tool designed to provide quick summaries and question-answering capabilities for various document types. It utilizes natural language processing to extract key information, generate concise summaries, answer user questions based on the document's content, and perform sentiment analysis. The project uses GPT-4o-mini model through the OpenAI API.

## Features

-   **File Upload and Processing:** Supports uploading and processing of PDF, DOCX, TXT, XLSX, JPEG, and PNG files.
-   **AI-Powered Summarization:** Generates concise summaries of uploaded documents using the GPT-4o-mini model.
-   **Question Answering:** Answers user questions based on the content of the uploaded documents, using relevant text retrieved via FAISS indexing and GPT-4o-mini.
-   **Sentiment Analysis:** Provides sentiment analysis of the uploaded text.
-   **User Interface:** Implemented using Streamlit, creating an easy-to-use and visually appealing interface.
## Screenshots

Screenshot of the Application
![Screenshot 2](https://github.com/user-attachments/assets/23d73d08-6fe9-4e3f-b83b-399e9e01eca1)

## Technologies Used

-   **Streamlit:** For building the web interface (`app.py`).
-   **FastAPI:** For creating the backend API (`main.py`).
-   **OpenAI GPT-4o-mini:** For text summarization, sentiment analysis, and question answering.
-   **Sentence Transformers:** For generating document embeddings.
-   **FAISS:** For efficient document retrieval.
-   **pdfplumber:** For extracting text from PDF files.
-   **docx2txt:** For extracting text from DOCX files.
-   **pandas:** For extracting text from Excel files.
-   **pytesseract:** For extracting text from images (OCR).
-   **python-docx:** For docx file processing.
-   **Pillow (PIL):** For image processing.
-   **python-dotenv:** For loading environment variables.
-   **uvicorn:** ASGI server for running FastAPI.

## Setup Instructions

### Prerequisites

-   Python 3.7+
-   pip

### Installation

1.  **Clone the repository:**

    ```
    git clone [<repository-url>](https://github.com/vagdevi424/SumItUpBot-SnapQA-with-AI-Power.git)
    cd SumItUpBot-SnapQA-with-AI-Power
    ```

2.  **Create a virtual environment:**

    ```
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    -   Create a `.env` file in the root directory.
    -   Add your OpenAI API key to the `.env` file:

        ```
        OPENAI_API_KEY=YOUR_OPENAI_API_KEY
        ```

### Usage

1.  **Run the FastAPI backend:**

    ```
    uvicorn main:app --reload
    ```

    This starts the backend server on `http://0.0.0.0:8000`.

2.  **Run the Streamlit frontend:**

    ```
    streamlit run app.py
    ```

    This starts the Streamlit app, which you can access in your browser (usually at `http://localhost:8501`).

### Endpoints

-   **POST `/upload/`:** Handles file uploads, extracts text, stores it in FAISS, and generates a summary.
-   **POST `/qa/`:** Answers questions based on the content of the uploaded document.




 
