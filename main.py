import os
import PyPDF2
import fitz  # PyMuPDF for image extraction
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from typing import List
from typing_extensions import Annotated, TypedDict
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

app = FastAPI()

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Flashcard Generator API! Use the /generate-flashcards endpoint to upload a PDF and generate flashcards."}


# Define the Flashcard structure
class Flashcard(TypedDict):
    """Flashcard for learning."""
    question: Annotated[str, "The question or prompt on the front of the flashcard"]
    answer: Annotated[str, "The answer or explanation on the back of the flashcard"]
    importance: Annotated[int, "How important this concept is, from 1 to 10"]
    image_path: Annotated[str, "Path to the associated image, if any"]

# A set of flashcards
class FlashcardSet(TypedDict):
    """Set of flashcards."""
    flashcards: Annotated[List[Flashcard], "A list of flashcards based on the input text"]

# Function to extract text from a PDF using PyPDF2
def extract_text_from_pdf(pdf_path: str) -> str:
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

# Function to extract images from the PDF using PyMuPDF
def extract_images_from_pdf(pdf_path: str, output_folder: str = "extracted_images") -> list:
    """Extracts images from a PDF and saves them to the specified folder."""
    os.makedirs(output_folder, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    image_paths = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        images = page.get_images(full=True)
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"page{page_number + 1}_img{img_index + 1}.{image_ext}"
            image_path = os.path.join(output_folder, image_filename)

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            image_paths.append(image_path)
    
    doc.close()
    return image_paths

# Set up the LLM
llm = ChatGroq(temperature=0, model="llama3-groq-70b-8192-tool-use-preview")
structured_llm = llm.with_structured_output(FlashcardSet)

# Define prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a set of flashcards from the given text. Focus on key concepts and important information."),
    ("human", "Text: {chunk}\n\nGenerate a list of flashcards based on this text.")
])

# Endpoint to upload PDF and generate flashcards
@app.post("/generate-flashcards/")
async def generate_flashcards(file: UploadFile = File(...)):
    # Save the uploaded PDF to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(await file.read())
        pdf_path = tmp_pdf.name

    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)

    # Split the document into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100)
    chunks = text_splitter.split_text(pdf_text)

    # Extract images from the PDF
    extracted_images = extract_images_from_pdf(pdf_path)

    # Initialize a list to store all flashcards
    all_flashcards = []
    image_index = 0

    # Generate flashcards and add images if available
    for chunk in chunks:
        if chunk.strip():  # Check if the chunk is not empty
            try:
                response = structured_llm.invoke(prompt.format(chunk=chunk))
                if 'flashcards' in response:
                    for flashcard in response['flashcards']:
                        # Attach an image to the flashcard if available
                        if image_index < len(extracted_images):
                            flashcard['image_path'] = extracted_images[image_index]
                            image_index += 1
                        else:
                            flashcard['image_path'] = None  # No image available
                        all_flashcards.append(flashcard)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error generating flashcards for chunk: {e}")

    # Clean up the temporary files
    os.remove(pdf_path)

    # Return the generated flashcards
    return {"flashcards": all_flashcards}
