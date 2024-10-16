import os
from langchain_community.document_loaders import WebBaseLoader
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

# Function to extract text from the webpage using the webpage's url
def extract_text_from_webpath(web_link: str) -> str:
     loader = WebBaseLoader(web_link)
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

# Extract text from the PDF
web_link = ""  # Adjust the path to your document
web_text = extract_text_from_webpath(web_link)

# Split the document into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100)
chunks = text_splitter.split_text(web_text[0].page_content)

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
