import os
from typing_extensions import Annotated, TypedDict, List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import PyPDF2
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

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

# Function to extract text from a PDF using PyPDF2
def extract_text_from_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# Set up the LLM
llm = ChatGroq(temperature=0, model="llama3-groq-70b-8192-tool-use-preview")
structured_llm = llm.with_structured_output(FlashcardSet)

# Define prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a set of flashcards from the given text. Focus on key concepts and important information."),
    ("human", "Text: {chunk}\n\nGenerate a list of flashcards based on this text.")
])

@app.post("/upload/")
async def create_flashcards(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Read the file as a binary stream
    pdf_text = extract_text_from_pdf(file.file)

    # Split the document into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100)
    chunks = text_splitter.split_text(pdf_text)

    all_flashcards = []

    for chunk in chunks:
        if chunk.strip():  # Check if the chunk is not empty
            try:
                response = structured_llm.invoke(prompt.format(chunk=chunk))
                if 'flashcards' in response:
                    all_flashcards.extend(response['flashcards'])
            except Exception as e:
                print(f"Error generating flashcards for chunk: {e}")

    return JSONResponse(content={"flashcards": all_flashcards})

# Run the server with: uvicorn api:app --reload
