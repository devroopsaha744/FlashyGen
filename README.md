# Memory AI

Memory AI is a flashcard generation tool that allows users to create flashcards from various input sources, including text, PDF, PPTX, DOCX, and CSV files. This project is powered by FastAPI for the backend and deployed on Vercel for the frontend.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

- Generate flashcards from different file formats and raw text.
- Supports PDF, PPTX, DOCX, CSV, and plain text inputs.
- Easy-to-use interface for flashcard generation.

## Technologies Used

- **Backend**: FastAPI
- **Frontend**: HTML, CSS (deployed on Vercel)
- **Text Extraction Libraries**: PyPDF2, python-pptx, python-docx, and csv
- **Environment Management**: dotenv
- **Generative AI**: LangChain
- **Deployment**: Vercel for the frontend, FastAPI for the backend

## Getting Started

To run the project locally, follow these steps:

### Prerequisites

- Python 3.7 or higher
- Node.js and npm (for Vercel deployment)
- A Groq API key (sign up for access if needed)

### Clone the Repository

```bash
git clone https://github.com/devroopsaha744/mermory-ai.git
cd mermory-ai
```

### Install Backend Dependencies

Navigate to the backend directory and install the required packages:

```bash
cd backend  # Update this if your backend is in a different folder
pip install -r requirements.txt
```

### Set Up Environment Variables

Create a `.env` file in the backend directory and add your Groq API key:

```plaintext
GROQ_API_KEY=your_api_key_here
```

### Run the FastAPI Backend

Start the FastAPI server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Deploy the Frontend on Vercel

1. Install the Vercel CLI if you haven't already:

   ```bash
   npm install -g vercel
   ```

2. Navigate to your frontend directory and deploy:

   ```bash
   cd frontend  # Update this if your frontend is in a different folder
   vercel
   ```

## API Documentation

Refer to the "api_docs.md" file for detailed information about the available endpoints and how to use them.

## Contributing

Contributions are welcome! Please follow these steps to contribute to the project:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.


