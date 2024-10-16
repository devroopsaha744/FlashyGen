import os
from typing_extensions import Annotated, TypedDict, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import PyPDF2
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import YoutubeLoader
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

# Function to extract transcript from a YouTube video
def extract_text_from_yt(link_path: str) -> str:
    loader = YoutubeLoader.from_youtube_url(
    link_path, add_video_info=False
)
    txt=  loader.load()
    return txt[0].page_content

# Set up the LLM
llm = ChatGroq(temperature=0, model="llama3-groq-70b-8192-tool-use-preview")
structured_llm = llm.with_structured_output(FlashcardSet)

# Define prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a set of flashcards from the given text. Focus on key concepts and important information."),
    ("human", "Text: {chunk}\n\nGenerate a list of flashcards based on this text.")
])

@app.post("/upload/")
async def create_flashcards(
    link: str = Form(None), 
    file: UploadFile = File(None)
):
    # Check if both file and link are provided
    if not (file or link):
        raise HTTPException(status_code=400, detail="Provide either a PDF file or a YouTube link.")

    all_flashcards = []

    if file:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        
        # Read the file as a binary stream
        pdf_text = extract_text_from_pdf(file.file)

        # Split the document into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100)
        chunks = text_splitter.split_text(pdf_text)

        for chunk in chunks:
            if chunk.strip():  # Check if the chunk is not empty
                try:
                    response = structured_llm.invoke(prompt.format(chunk=chunk))
                    if 'flashcards' in response:
                        all_flashcards.extend(response['flashcards'])
                except Exception as e:
                    print(f"Error generating flashcards for PDF chunk: {e}")

    elif link:
        # Extract text from YouTube video
        try:
            yt_text = extract_text_from_yt(link)
            # Split the YouTube transcript into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100)
            chunks = text_splitter.split_text(yt_text)

            for chunk in chunks:
                if chunk.strip():  # Check if the chunk is not empty
                    try:
                        response = structured_llm.invoke(prompt.format(chunk=chunk))
                        if 'flashcards' in response:
                            all_flashcards.extend(response['flashcards'])
                    except Exception as e:
                        print(f"Error generating flashcards for YouTube chunk: {e}")

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error extracting text from YouTube video: {e}")

    return JSONResponse(content={"flashcards": all_flashcards})

# Run the server with: uvicorn api:app --reload
