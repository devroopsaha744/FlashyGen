import os
import PyPDF2
import fitz  # PyMuPDF for image extraction
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from typing_extensions import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

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
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Open the PDF
    doc = fitz.open(pdf_path)
    image_paths = []

    # Iterate through each page
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        images = page.get_images(full=True)
        
        # Extract images
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"page{page_number + 1}_img{img_index + 1}.{image_ext}"
            image_path = os.path.join(output_folder, image_filename)

            # Save the image
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            # Keep track of the image path
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

# Extract text from the PDF
pdf_path = "study/DA-unit 1 part 2.pdf"  # Adjust the path to your document
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
            print(f"Error generating flashcards for chunk: {e}")
    else:
        print("Empty chunk detected, skipping...")

# Print the generated flashcards
print("\nGenerated Flashcards:")
for i, card in enumerate(all_flashcards, 1):
    print(f"\nFlashcard {i}:")
    print(f"Question: {card['question']}")
    print(f"Answer: {card['answer']}")
    if card['image_path']:
        print(f"Image: {card['image_path']}")
    else:
        print("No image associated.")
