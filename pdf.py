import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from typing_extensions import Annotated, TypedDict
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

# Load the document
doc_path = "Datawarehousenotes_1.pdf"  # Adjust the path to your document
loader = PyPDFLoader(doc_path)
document = loader.load()

# Split document into chunks
chunk_size = 1000
chunk_overlap = 200
text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
chunks = text_splitter.split_documents(document)

# Set up the LLM
llm = ChatGroq(temperature=0, model="llama3-70b-8192")
structured_llm = llm.with_structured_output(Flashcard)

# Define prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a flashcard from the given text. Focus on key concepts and important information."),
    ("human", "Text: {chunk_text}\n\nGenerate a flashcard based on this text.")
])

# Function to generate flashcards
def generate_flashcards(chunks, num_cards=5):
    flashcards = []
    for chunk in chunks[:num_cards]:  # Limit to num_cards to avoid excessive API calls
        chunk_text = chunk.page_content
        response = structured_llm.invoke(prompt.format(chunk_text=chunk_text))
        flashcards.append(response)
    return flashcards

# Generate flashcards
flashcards = generate_flashcards(chunks)

# Print the generated flashcards
for i, card in enumerate(flashcards, 1):
    print(f"\nFlashcard {i}:")
    print(f"Question: {card['question']}")
    print(f"Answer: {card['answer']}")
    print(f"Importance: {card['importance']}")
