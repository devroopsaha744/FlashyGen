import os
from docx import Document
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from typing_extensions import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Define the Cloze Deletion Flashcard structure
class ClozeDeletionFlashcard(TypedDict):
    """Flashcard for cloze deletion."""
    question_with_blanks: Annotated[str, "A sentence with one or more blanks (____) for the learner to fill in."]
    correct_answers: Annotated[List[str], "The list of correct words or phrases that fill in the blanks."]

# A set of cloze deletion flashcards
class ClozeDeletionFlashcardSet(TypedDict):
    """Set of cloze deletion flashcards."""
    flashcards: Annotated[List[ClozeDeletionFlashcard], "A list of fill-in-the-blank flashcards based on the input text."]

# Function to extract text from a Word document (.docx) using python-docx
def extract_text_from_word(docx_path: str) -> str:
    document = Document(docx_path)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"
    return text

# Set up the LLM
llm = ChatGroq(temperature=0, model="llama3-8b-8192")
structured_llm = llm.with_structured_output(ClozeDeletionFlashcardSet)

# Define the prompt for cloze deletion flashcards
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "Generate a set of cloze deletion flashcards from the given text. "
     "Focus on creating simple fill-in-the-blank questions for key facts or important information."),
    ("human", 
     "Text: {chunk}\n\nCreate flashcards using simple cloze deletions. For each flashcard, replace key information with blanks (____) "
     "to test the learner's memory. Provide the correct word or phrase for each blank in the answer.")
])

# Extract text from the PDF
pdf_path = "study\genghis khan sample.docx"  # Adjust the path to your document
pdf_text = extract_text_from_word(pdf_path)

# Split the document into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100)
chunks = text_splitter.split_text(pdf_text)

# Initialize a list to store cloze deletion flashcards
cloze_flashcards = []

for chunk in chunks:
    if chunk.strip():  # Check if the chunk is not empty
        try:
            response = structured_llm.invoke(prompt.format(chunk=chunk))
            if 'flashcards' in response:
                for flashcard in response['flashcards']:
                    # Ensure that the flashcard has both a question with blanks and answers
                    if 'question_with_blanks' in flashcard and 'correct_answers' in flashcard:
                        cloze_flashcards.append(flashcard)
        except Exception as e:
            print(f"Error generating cloze deletion flashcards for chunk: {e}")
    else:
        print("Empty chunk detected, skipping...")

# Print the generated cloze deletion flashcards
print("\nGenerated Cloze Deletion Flashcards:")
for i, card in enumerate(cloze_flashcards, 1):
    print(f"\nFlashcard {i}:")
    print(f"Question: {card['question_with_blanks']}")
    print(f"Answer: {', '.join(card['correct_answers'])}")
