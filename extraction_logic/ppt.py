import os
from pptx import Presentation
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

# Function to extract text from a PowerPoint presentation (.pptx) using python-pptx
def extract_text_from_pptx(pptx_path: str) -> str:
    presentation = Presentation(pptx_path)
    text = ""
    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text + "\n"
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
ppt_path = ""  # Adjust the path to your document
ppt_text = extract_text_from_pptx(ppt_path)

# Split the document into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100)
chunks = text_splitter.split_text(ppt_text)

# Initialize a list to store all flashcards
all_flashcards = []

for chunk in chunks:
    if chunk.strip():  # Check if the chunk is not empty
        try:
            response = structured_llm.invoke(prompt.format(chunk=chunk))
            if 'flashcards' in response:
                all_flashcards.extend(response['flashcards'])
        except Exception as e:
            print(f"Error generating flashcards for chunk")
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
