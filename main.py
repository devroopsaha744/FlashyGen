import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing_extensions import Annotated, TypedDict, List
from typing import List, Optional
from dotenv import load_dotenv
import PyPDF2
import pptx  # For PPTX extraction
import docx  # For DOCX extraction
import csv   # For CSV extraction
import io
from io import BytesIO
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import YoutubeLoader

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Set up FastAPI
app = FastAPI()

# Enable CORS for all origins, can be restricted in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Flashcard(TypedDict):
    """Flashcard for learning."""
    question: Annotated[str, "The question or prompt on the front of the flashcard"]
    answer: Annotated[str, "The answer or explanation on the back of the flashcard"]

# A set of flashcards
class FlashcardSet(TypedDict):
    """Set of flashcards."""
    flashcards: Annotated[List[Flashcard], "A list of flashcards based on the input text"]


# Text extraction functions
def extract_text_from_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_pptx(file) -> str:
    # Convert the SpooledTemporaryFile to a BytesIO stream
    file_bytes = BytesIO(file.read())
    presentation = pptx.Presentation(file_bytes)
    text = ""
    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
    file.seek(0)  # Reset file pointer after reading
    return text

def extract_text_from_docx(file) -> str:
    # Convert the SpooledTemporaryFile to a BytesIO stream
    file_bytes = BytesIO(file.read())
    doc = docx.Document(file_bytes)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    file.seek(0)  # Reset file pointer after reading
    return text


def extract_text_from_csv(file) -> str:
    # Decode the bytes to a string and then use io.StringIO to create a text stream
    decoded_file = io.StringIO(file.read().decode("utf-8"))
    text = ""
    reader = csv.reader(decoded_file)
    for row in reader:
        text += " ".join(row) + "\n"
    file.seek(0)  # Reset file pointer after reading
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
@app.get("/")
def read_root():
    return {"message": "Welcome to the flashcard generation prototype!"}

@app.post("/flashcard/")
async def create_flashcards(
    method: str = Form(...),
    link: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
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

    return {"flashcards": all_flashcards}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
