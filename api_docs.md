# Flashcard Generation API Documentation

## Overview
This API allows users to generate flashcards from various input sources, including text, PDF, PPTX, DOCX, and CSV files. The generated flashcards consist of questions and answers focusing on key concepts from the input text, with support for both traditional and cloze deletion formats.

## Base URL
```
https://flashcard-generator-mdhf.onrender.com/
```

## Endpoints

### 1. Flashcard Generation

- **POST /flashcard/**

  Generates flashcards based on the provided input method and type.

  **Request Body:**
  - `method` (string, required): The method of input (options: `pdf`, `pptx`, `docx`, `csv`, `text`).
  - `type` (string, required): The type of flashcards to generate (options: `type-I` for traditional, `type-II` for cloze deletion).
  - `text` (string, optional): The text input (required if `method` is `text`).
  - `file` (file, optional): The file to upload (required for `pdf`, `pptx`, `docx`, and `csv` methods).

  **Request Example:**
  ```plaintext
  POST /flashcard/
  Content-Type: multipart/form-data

  method: pdf
  type: type-I
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

  For cloze deletion flashcards (type-II), the response will be:
  ```json
  {
    "flashcards": [
      {
        "question_with_blanks": "______ is a programming language.",
        "correct_answers": ["Python"]
      },
      ...
    ]
  }
  ```

  **Error Responses:**
  - **400 Bad Request**
    - If the file format is incorrect or missing.
    - If text is not provided when required.
    - If an invalid method is specified.
  - **500 Internal Server Error**
    - If there's an error processing the request.

## Supported Input Methods

1. **PDF**
   - **Description**: Upload a `.pdf` file to extract text and generate flashcards.
   - **File Type**: `.pdf`
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: pdf
     type: type-I
     file: <PDF file>
     ```

2. **PPTX**
   - **Description**: Upload a `.pptx` file to extract text from slides and generate flashcards.
   - **File Type**: `.pptx`
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: pptx
     type: type-I
     file: <PPTX file>
     ```

3. **DOCX**
   - **Description**: Upload a `.docx` file to extract text from paragraphs and generate flashcards.
   - **File Type**: `.docx`
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: docx
     type: type-II
     file: <DOCX file>
     ```

4. **CSV**
   - **Description**: Upload a `.csv` file to extract data and generate flashcards.
   - **File Type**: `.csv`
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: csv
     type: type-I
     file: <CSV file>
     ```

5. **Text**
   - **Description**: Provide raw text input for flashcard generation.
   - **Example Request**:
     ```plaintext
     POST /flashcard/
     method: text
     type: type-II
     text: "This is a sample text for flashcard generation."
     ```

## Flashcard Types

1. **Traditional (type-I)**
   - Consists of a question and an answer pair.
   - Suitable for direct question-answer style learning.

2. **Cloze Deletion (type-II)**
   - Presents a sentence with blanks and the correct answers to fill those blanks.
   - Ideal for context-based learning and fill-in-the-blank exercises.

## Notes
- Ensure that the file formats, methods, and flashcard types are correctly specified to avoid errors.
- The API will return a list of flashcards generated from the provided input, formatted according to the specified type.
- The server is hosted on Render, so the base URL is https://flashcard-generator-mdhf.onrender.com/.