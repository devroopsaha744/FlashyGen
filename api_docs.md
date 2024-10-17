# Flashcard Generation API Documentation

## Overview
This API allows users to generate flashcards from various input sources, including text, PDF, PPTX, DOCX, and CSV files. The generated flashcards consist of questions and answers focusing on key concepts from the input text.

## Base URL
```
http://<your_host>:8000/
```

## Endpoints

### 1. Root Endpoint

- **GET /**

  Returns a welcome message.

  **Response:**
  ```json
  {
    "message": "Welcome to the flashcard generation prototype!"
  }
  ```

### 2. Flashcard Generation

- **POST /flashcard/**

  Generates flashcards based on the provided input method.

  **Request Body:**
  - `method` (string, required): The method of input (options: `pdf`, `pptx`, `docx`, `csv`, `text`).
  - `text` (string, optional): The text input (required if `method` is `text`).
  - `file` (file, optional): The file to upload (required based on the method).

  **Request Example:**
  ```plaintext
  POST /flashcard/
  Content-Type: multipart/form-data

  method: pdf
  file: <PDF file>
  ```

  **Response:**
  Returns a list of generated flashcards.
  ```json
  {
    "flashcards": [
      {
        "question": "What is...?",
        "answer": "..."
      },
      ...
    ]
  }
  ```

  **Error Responses:**
  - **400 Bad Request**
    - If the file format is incorrect or missing:
      ```json
      {
        "detail": "Please upload a valid PDF file."
      }
      ```
    - If text is not provided when required:
      ```json
      {
        "detail": "Please provide valid text input."
      }
      ```
    - If an invalid method is specified:
      ```json
      {
        "detail": "Invalid method specified."
      }
      ```

## Supported Input Methods

1. **PDF**
   - **Description**: Upload a `.pdf` file to extract text and generate flashcards.
   - **File Type**: `.pdf`
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: pdf
     file: <PDF file>
     ```

2. **PPTX**
   - **Description**: Upload a `.pptx` file to extract text from slides and generate flashcards.
   - **File Type**: `.pptx`
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: pptx
     file: <PPTX file>
     ```

3. **DOCX**
   - **Description**: Upload a `.docx` file to extract text from paragraphs and generate flashcards.
   - **File Type**: `.docx`
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: docx
     file: <DOCX file>
     ```

4. **CSV**
   - **Description**: Upload a `.csv` file to extract data and generate flashcards.
   - **File Type**: `.csv`
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: csv
     file: <CSV file>
     ```

5. **Text**
   - **Description**: Provide raw text input for flashcard generation.
   - **Request Body**:
     - `text`: The text input (required).
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: text
     text: "This is a sample text for flashcard generation."
     ```

## Environment Variables
- `GROQ_API_KEY`: Your API key for Groq, needed for LLM interactions.

## Notes
- Ensure that the file formats and methods are correctly specified to avoid errors.
- The API will return a list of flashcards generated from the provided input.

## Running the API
To run the API locally, use the following command:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

