import os
import json
import shutil
import time
import re
from pathlib import Path
from pdfminer.high_level import extract_text
from docx import Document
import pdfplumber  # For layout parsing of PDFs

# Define directories
DOCS_FOLDER = "D:/Code/Projects/Legal Insight/docs"
PROCESSED_FOLDER = "D:/Code/Projects/Legal Insight/data/processed"
ARCHIVE_FOLDER = 'D:/Code/Projects/Legal Insight/data/processed/archive'  # Corrected this path

# Ensure processed and archive folders exist
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

def extract_text_from_docx(file_path):
    """Extract text from a .docx file."""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file_path):
    """Extract text from a PDF using pdfplumber for layout-aware parsing."""
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_file(file_path):
    """Extract text from various document types."""
    file_ext = Path(file_path).suffix.lower()

    if file_ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_ext == ".docx":
        return extract_text_from_docx(file_path)
    elif file_ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return None  # Unsupported file type

def clean_text(text):
    """Clean and normalize text by removing noise and standardizing."""
    # Remove unwanted characters (e.g., non-ASCII, extra spaces, etc.)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = text.strip()  # Remove leading and trailing spaces
    
    # Normalize common date formats and other terms if needed
    text = re.sub(r'(\d{2})/(\d{2})/(\d{4})', r'\3-\1-\2', text)  # Convert date format to yyyy-mm-dd

    return text

def update_status(message):
    """Write status updates to a JSON file."""
    STATUS_FILE = "D:/Code/Projects/Legal Insight/data/status.json"
    
    # Read existing status if it exists
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            status_data = json.load(f)
    else:
        status_data = {}

    # Append new message with timestamp or update
    status_data["status"] = message
    status_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=4)

def segment_text(text):
    """Segment the extracted text into logical blocks, such as clauses or sections."""
    # Split text into logical sections based on headings or other markers (you may adjust this for your docs)
    sections = re.split(r'(Section \d+|Clause \d+|Article \d+)', text)
    segmented_text = []
    current_section = ""
    
    for part in sections:
        if part.strip():
            if re.match(r'(Section \d+|Clause \d+|Article \d+)', part):
                if current_section:
                    segmented_text.append(current_section.strip())
                current_section = part
            else:
                current_section += " " + part.strip()
    
    if current_section:
        segmented_text.append(current_section.strip())
    
    return segmented_text

def organize_extracted_data(file_name, text):
    """Organize extracted text into a structured JSON format."""
    # Segment the text into logical blocks (sections/clauses)
    segmented_text = segment_text(text)

    # Example structure (you can customize this as per your document type)
    document_data = {
        "document_name": file_name,
        "content": segmented_text,
        "metadata": {
            "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": os.path.join(DOCS_FOLDER, file_name)
        }
    }

    return document_data

def process_documents():
    """Process all documents in the docs folder and save extracted and cleaned data."""
    update_status("Parsing started...")

    for file_name in os.listdir(DOCS_FOLDER):
        file_path = os.path.join(DOCS_FOLDER, file_name)

        if os.path.isfile(file_path):
            extracted_text = extract_text_from_file(file_path)

            if extracted_text:
                cleaned_text = clean_text(extracted_text)
                document_data = organize_extracted_data(file_name, cleaned_text)
                
                # Save extracted data as structured JSON
                output_path = os.path.join(PROCESSED_FOLDER, f"{Path(file_name).stem}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(document_data, f, ensure_ascii=False, indent=4)

                # Move the processed file to the archive folder
                try:
                    shutil.move(file_path, os.path.join(ARCHIVE_FOLDER, file_name))
                    update_status(f"Moved file {file_name} to archive.")
                except Exception as e:
                    update_status(f"Error moving {file_name}: {str(e)}")

    update_status("Parsing completed!")
    return {"message": "Parsing completed"}

if __name__ == "__main__":
    process_documents()
