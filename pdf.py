import os
import PyPDF2
import base64
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

# Initialize a list to store all flashcards
all_flashcards = []

# Generate flashcards and add images if available
for chunk in chunks:
    if chunk.strip():  # Check if the chunk is not empty
            response = structured_llm.invoke(prompt.format(chunk=chunk))
            if 'flashcards' in response:
                    all_flashcards.extend(response['flashcards'])
    else:
        print("Empty chunk detected, skipping...")

# Print the generated flashcards
print("\nGenerated Flashcards:")
for i, card in enumerate(all_flashcards, 1):
    print(f"\nFlashcard {i}:")
    print(f"Question: {card['question']}")
    print(f"Answer: {card['answer']}")
    if card['image_data']:
        print(f"Image Data (Base64): {card['image_data'][:20]}...")  # Print only the first 100 characters
    else:
        print("No image associated.")
