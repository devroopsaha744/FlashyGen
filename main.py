import os
from typing_extensions import Annotated, TypedDict, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import PyPDF2
import pptx  # For PPTX extraction
import docx  # For DOCX extraction
import csv   # For CSV extraction
import requests
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import YoutubeLoader
from langchain.document_loaders import WebBaseLoader

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Set up FastAPI
app = FastAPI()

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the Flashcard structure
class Flashcard(TypedDict):
    question: Annotated[str, "The question or prompt on the front of the flashcard"]
    answer: Annotated[str, "The answer or explanation on the back of the flashcard"]

class FlashcardSet(TypedDict):
    flashcards: Annotated[List[Flashcard], "A list of flashcards based on the input text"]

# Text extraction functions
def extract_text_from_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_pptx(file) -> str:
    presentation = pptx.Presentation(file)
    text = ""
    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    return text

def extract_text_from_docx(file) -> str:
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_csv(file) -> str:
    text = ""
    reader = csv.reader(file)
    for row in reader:
        text += " ".join(row) + "\n"
    return text


def extract_text_from_youtube(link_path: str) -> str:
    loader = YoutubeLoader.from_youtube_url(link_path, add_video_info=False)
    txt = loader.load()
    return txt

# Set up the LLM
llm = ChatGroq(temperature=0, model="llama3-groq-70b-8192-tool-use-preview")
structured_llm = llm.with_structured_output(FlashcardSet)

# Define prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a set of flashcards from the given text. Focus on key concepts and important information."),
    ("human", "Text: {chunk}\n\nGenerate a list of flashcards based on this text.")
])

@app.post("/flashcard/")
async def create_flashcards(
    method: str = Form(...),  # Method can be 'pdf', 'pptx', 'docx', 'csv', 'webpage', 'youtube', or 'text'
    link: str = Form(None), 
    file: UploadFile = File(None),
    text: str = Form(None)
):
    all_flashcards = []

    # Extraction and splitting based on the method
    if method == "pdf":
        if not file or not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Please upload a valid PDF file.")
        pdf_text = extract_text_from_pdf(file.file)
        chunks = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100).split_text(pdf_text)

    elif method == "pptx":
        if not file or not file.filename.endswith(".pptx"):
            raise HTTPException(status_code=400, detail="Please upload a valid PPTX file.")
        pptx_text = extract_text_from_pptx(file.file)
        chunks = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100).split_text(pptx_text)

    elif method == "docx":
        if not file or not file.filename.endswith(".docx"):
            raise HTTPException(status_code=400, detail="Please upload a valid DOCX file.")
        docx_text = extract_text_from_docx(file.file)
        chunks = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100).split_text(docx_text)

    elif method == "csv":
        if not file or not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Please upload a valid CSV file.")
        csv_text = extract_text_from_csv(file.file)
        chunks = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100).split_text(csv_text)

    elif method == "youtube":
        if not link:
            raise HTTPException(status_code=400, detail="Please provide a valid YouTube link.")
        youtube_text = extract_text_from_youtube(link)
        chunks = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100).split_text(youtube_text[0].page_content)

    elif method == "text":
        if not text:
            raise HTTPException(status_code=400, detail="Please provide valid text input.")
        chunks = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100).split_text(text)

    else:
        raise HTTPException(status_code=400, detail="Invalid method specified.")

    # Generate flashcards for the extracted chunks
    for chunk in chunks:
        if chunk.strip():
            try:
                response = structured_llm.invoke(prompt.format(chunk=chunk))
                if 'flashcards' in response:
                    all_flashcards.extend(response['flashcards'])
            except Exception as e:
                print(f"Error generating flashcards for chunk: {e}")

    return JSONResponse(content={"flashcards": all_flashcards})

# Run the server with: uvicorn api:app --reload
