import os
import PyPDF2
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from typing_extensions import Annotated, TypedDict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Define the Flashcard structure
class Flashcard(TypedDict):
    """Flashcard for learning."""
    question: Annotated[str, "The question or prompt on the front of the flashcard"]
    answer: Annotated[str, "The answer or explanation on the back of the flashcard"]
    importance: Annotated[int, "How important this concept is, from 1 to 10"]

#A set of flashcards
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
llm = ChatGroq(temperature=0, model="llama3-70b-8192")
structured_llm = llm.with_structured_output(FlashcardSet)

# Define prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a set of flashcards from the given text. Focus on key concepts and important information."),
    ("human", "Text: {pdf_text}\n\nGenerate a list of flashcards based on this entire text.")
])

# Extract text from the PDF
pdf_path = "Unit-1 Introduction to Data Analytics.pdf"  # Adjust the path to your document
pdf_text = extract_text_from_pdf(pdf_path)

# Generate flashcards from the entire document
response = structured_llm.invoke(prompt.format(pdf_text=pdf_text))

# Print the generated flashcards
print("\nGenerated Flashcards:")
for i, card in enumerate(response['flashcards'], 1):
    print(f"\nFlashcard {i}:")
    print(f"Question: {card['question']}")
    print(f"Answer: {card['answer']}")

