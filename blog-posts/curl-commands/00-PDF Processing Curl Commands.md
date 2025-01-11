A comprehensive guide for testing these endpoints with curl commands:

# Testing Your PDF Processor with Curl Commands

In this guide, we'll walk through how to test each PDF processing function using curl commands. These commands will help you verify that your PDF processor is working correctly.

## Prerequisites
- curl installed on your system
- A PDF file for testing (let's call it 'sample.pdf')
- Your FastAPI server running (usually at http://localhost:8000)

## 1. Extract Text from PDF

This command uploads a PDF and gets its text content:

```bash
curl -X POST \
  http://localhost:8000/pdf/extract-text \
  -H "Content-Type: multipart/form-data" \
  -F "file=@./personal_project_notes/NASM_CPT7_Study_Guide.pdf" \
  | json_pp
```

Expected successful response:
```json
{
   "status": "success",
   "message": "Text extracted successfully",
   "details": {
      "filename": "sample.pdf",
      "text": "Your PDF content will appear here...",
      "character_count": 1234
   }
}
```

## 2. Get PDF Metadata

This command retrieves metadata from your PDF:

```bash
curl -X POST \
  http://localhost:8000/pdf/metadata \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/sample.pdf" \
  | json_pp
```

Expected successful response:
```json
{
   "status": "success",
   "message": "Metadata extracted successfully",
   "details": {
      "filename": "sample.pdf",
      "metadata": {
         "title": "Sample Document",
         "author": "John Doe",
         "creation_date": "2024-01-10T12:34:56",
         "page_count": 5
      }
   }
}
```

## 3. Full PDF Analysis

This command performs both text extraction and metadata analysis:

```bash
curl -X POST \
  http://localhost:8000/pdf/analyze \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/sample.pdf" \
  | json_pp
```

Expected successful response:
```json
{
   "status": "success",
   "message": "PDF analysis completed successfully",
   "details": {
      "filename": "sample.pdf",
      "text": "Your PDF content will appear here...",
      "metadata": {
         "title": "Sample Document",
         "author": "John Doe",
         "creation_date": "2024-01-10T12:34:56",
         "page_count": 5
      },
      "character_count": 1234
   }
}
```

## Testing Error Cases

### 1. Testing with Non-PDF File

```bash
curl -X POST \
  http://localhost:8000/pdf/extract-text \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/not_a_pdf.txt" \
  | json_pp
```

Expected error response:
```json
{
   "detail": "File must be a PDF"
}
```

### 2. Testing with Missing File

```bash
curl -X POST \
  http://localhost:8000/pdf/extract-text \
  | json_pp
```

Expected error response:
```json
{
   "detail": "Field required"
}
```

## Helpful Testing Script

Here's a bash script you can use to test all endpoints:

```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Your PDF file path
PDF_FILE="/path/to/your/sample.pdf"

echo -e "${GREEN}Testing PDF Text Extraction...${NC}"
curl -s -X POST \
  http://localhost:8000/pdf/extract-text \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$PDF_FILE" \
  | json_pp

echo -e "\n${GREEN}Testing PDF Metadata Extraction...${NC}"
curl -s -X POST \
  http://localhost:8000/pdf/metadata \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$PDF_FILE" \
  | json_pp

echo -e "\n${GREEN}Testing Full PDF Analysis...${NC}"
curl -s -X POST \
  http://localhost:8000/pdf/analyze \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$PDF_FILE" \
  | json_pp
```

Save this as `test_pdf_endpoints.sh`, make it executable (`chmod +x test_pdf_endpoints.sh`), and run it:

```bash
./test_pdf_endpoints.sh
```

## Troubleshooting Tips

1. If you get "connection refused" errors:
   - Make sure your FastAPI server is running
   - Check the port number is correct

2. If you get "file not found" errors:
   - Double-check your file path
   - Make sure you have read permissions for the file

3. If you get "Internal Server Error":
   - Check your server logs for details
   - Make sure your PDF file isn't corrupted

## Monitoring the Logs

While testing, it's helpful to watch your application logs:

```bash
tail -f logs/app.log
```

This will show you detailed information about what's happening during PDF processing.