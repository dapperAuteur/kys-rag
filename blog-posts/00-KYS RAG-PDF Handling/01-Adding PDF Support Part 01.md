# Adding PDF Support to Science Decoder: Part 1 - Setting Up PDF Processing

Hey there! Today we're going to add PDF support to our Science Decoder tool. This is super important because most scientific papers come in PDF format. By the end of this tutorial, you'll have a solid foundation for working with PDFs in Python.

## What We'll Cover
1. Understanding PDF basics
2. Setting up our development environment
3. Creating a PDF processor class
4. Adding tests
5. Running and testing our code

## Prerequisites
- Basic Python knowledge
- Python 3.11 or higher installed
- A code editor (like VS Code)
- Basic understanding of async/await in Python

## Step 1: Understanding PDF Basics

Before we dive in, let's understand what a PDF file actually is. PDF (Portable Document Format) files are like digital paper - they keep their formatting no matter what device you use to view them. They can contain:
- Text
- Images
- Tables
- Metadata (information about the document)

## Step 2: Setting Up Our Environment

First, let's add the required packages to our `requirements.txt` file:

```bash
# Add these lines to requirements.txt
PyPDF2>=3.0.0
pdfplumber>=0.10.0
```

Now install the new requirements:

```bash
pip install -r requirements.txt
```

We're using two PDF libraries because each has its strengths:
- PyPDF2: Great for metadata and basic operations
- pdfplumber: Better at extracting text accurately

## Step 3: Creating the PDF Processor

We're going to create a new class called `PDFProcessor` that will handle all our PDF operations. Let's look at the key parts of our implementation:

### The Class Structure

Our `PDFProcessor` class does two main things:
1. Extracts text from PDFs
2. Gets metadata (like author, title, date created)

We've added type hints and logging to make the code more maintainable and easier to debug.

### Error Handling

We handle common problems like:
- Missing files
- Corrupted PDFs
- Invalid metadata

This makes our code more reliable in real-world use.

### Logging

We've added detailed logging that helps us track:
- When processing starts and ends
- How many pages were processed
- Any warnings or errors

## Step 4: Adding Tests

Testing is crucial for any production code. Our tests check:
- How the code handles missing files
- Date parsing functionality
- Basic error conditions

You can run the tests with:

```bash
pytest tests/services/test_pdf_processor.py -v
```

## Using the PDF Processor

Here's how to use our new PDF processor:

```python
from app.services.pdf_processor import pdf_processor

async def process_scientific_paper(file_path: str):
    try:
        # Extract text
        text = await pdf_processor.extract_text(file_path)
        print(f"Extracted {len(text)} characters")

        # Get metadata
        metadata = await pdf_processor.get_metadata(file_path)
        print(f"Found metadata: {metadata}")

    except Exception as e:
        print(f"Error processing PDF: {e}")
```

## Why This Matters For Your Portfolio

This code shows potential employers that you:
1. Think about error handling and logging
2. Write type-safe, maintainable code
3. Know how to work with external libraries
4. Understand async programming
5. Write tests for your code

## Next Steps

In the next tutorial, we'll:
1. Add file upload capabilities to our FastAPI backend
2. Create endpoints for processing uploaded PDFs
3. Store the extracted text in our database
4. Add search functionality for PDF content

Want to get ready? Here's what you can do:
1. Practice using the PDF processor with different PDF files
2. Read up on FastAPI file uploads
3. Think about how you'd store PDF content in MongoDB

Questions about this tutorial? Drop them in the comments below!

Remember: logging and error handling might seem like extra work, but they're what separate hobby projects from production-ready code. They show you're thinking about real-world usage.

Happy coding! 🚀

## Testing Your Setup

To make sure everything's working, try this:

```bash
# Run the tests
pytest tests/services/test_pdf_processor.py -v

# Check the logs
tail -f logs/app.log
```

You should see test results and detailed logs showing what the code is doing.

In the next post, we'll build on this foundation to handle PDF uploads through our API. Stay tuned!