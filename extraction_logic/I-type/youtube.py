import os
import PyPDF2
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from typing_extensions import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi
# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Define the Flashcard structure
class Flashcard(TypedDict):
    """Flashcard for learning."""
    question: Annotated[str, "The question or prompt on the front of the flashcard"]
    answer: Annotated[str, "The answer or explanation on the back of the flashcard"]
    importance: Annotated[int, "How important this concept is, from 1 to 10"]

# A set of flashcards
class FlashcardSet(TypedDict):
    """Set of flashcards."""
    flashcards: Annotated[List[Flashcard], "A list of flashcards based on the input text"]

# Function to extract text from a PDF using YoutubeLoader
def extract_text_from_yt(link_path: str) -> str:
    # Extract the video ID from the YouTube URL
    video_id = link_path.split("v=")[-1].split("&")[0]

    try:
        # Fetch the transcript using the YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Combine the text from the transcript into a single string
        text = " ".join([entry['text'] for entry in transcript])
        return text

    except Exception as e:
        # Handle cases where the transcript is not available
        print(f"Error fetching transcript: {e}")
        return ""

# Set up the LLM
llm = ChatGroq(temperature=0, model="llama3-groq-70b-8192-tool-use-preview")
structured_llm = llm.with_structured_output(FlashcardSet)

# Define prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate a set of flashcards from the given text. Focus on key concepts and important information."),
    ("human", "Text: {chunk}\n\nGenerate a list of flashcards based on this text.")
])

# Extract text from the PDF
link_path = "https://www.youtube.com/watch?v=okolv1y6IlE"  # organic chemistry sample video 
video_text = extract_text_from_yt(link_path)

# Split the document into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=100)
chunks = text_splitter.split_text(video_text)

# Initialize a list to store all flashcards
all_flashcards = []

for chunk in chunks:
    if chunk.strip():  # Check if the chunk is not empty
        try:
            response = structured_llm.invoke(prompt.format(chunk=chunk))
            if 'flashcards' in response:
                all_flashcards.extend(response['flashcards'])
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
