import os
import json
import shutil
import time
import re
from pathlib import Path
from pdfminer.high_level import extract_text
from docx import Document
import pdfplumber
import tika
from tika import parser

# Initialize Tika (Client-only mode for faster processing)
tika.TikaClientOnly = True
tika.initVM()

# Define directories
DOCS_FOLDER = "D:/Code/Projects/Legal Insight/docs"
PROCESSED_FOLDER = "D:/Code/Projects/Legal Insight/data/processed"
ARCHIVE_FOLDER = "D:/Code/Projects/Legal Insight/data/processed/archive"

# Ensure processed and archive folders exist
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

def extract_text_from_docx(file_path):
    """Extract text from a .docx file."""
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""

def extract_text_from_pdf_with_pdfplumber(file_path):
    """Extract text from a PDF using pdfplumber for layout-aware parsing."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        return text.strip()
    except Exception as e:
        print(f"pdfplumber failed for {file_path}: {e}")
        return ""

def extract_text_from_pdf_with_tika(file_path):
    """Extract text from a PDF using Tika for OCR and better structured extraction."""
    try:
        raw = parser.from_file(file_path)
        return raw.get('content', '').strip()
    except Exception as e:
        print(f"Tika failed for {file_path}: {e}")
        return ""

def extract_text_from_file(file_path):
    """Extract text from various document formats."""
    file_ext = Path(file_path).suffix.lower()

    if file_ext == ".pdf":
        text = extract_text_from_pdf_with_pdfplumber(file_path)
        if not text:  # Fallback to Tika if pdfplumber fails
            text = extract_text_from_pdf_with_tika(file_path)
        return text
    elif file_ext == ".docx":
        return extract_text_from_docx(file_path)
    elif file_ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    else:
        print(f"Unsupported file type: {file_ext}")
        return ""

def clean_text(text):
    """Clean extracted text by removing noise and standardizing formatting."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove excessive spaces
    text = re.sub(r'(\d{2})/(\d{2})/(\d{4})', r'\3-\1-\2', text)  # Normalize date format (DD/MM/YYYY → YYYY-MM-DD)
    return text

def update_status(message):
    """Update the status JSON file with the latest processing status."""
    STATUS_FILE = "D:/Code/Projects/Legal Insight/data/status.json"
    
    status_data = {}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            try:
                status_data = json.load(f)
            except json.JSONDecodeError:
                pass

    status_data["status"] = message
    status_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=4)

def segment_text(text):
    """Segment text into structured sections based on headings or common markers."""
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
    segmented_text = segment_text(text)
    
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
    """Process all documents in the docs folder."""
    update_status("Parsing started...")

    for file_name in os.listdir(DOCS_FOLDER):
        file_path = os.path.join(DOCS_FOLDER, file_name)

        if os.path.isfile(file_path):
            extracted_text = extract_text_from_file(file_path)

            if extracted_text:
                cleaned_text = clean_text(extracted_text)
                document_data = organize_extracted_data(file_name, cleaned_text)
                
                output_path = os.path.join(PROCESSED_FOLDER, f"{Path(file_name).stem}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(document_data, f, ensure_ascii=False, indent=4)

                shutil.move(file_path, os.path.join(ARCHIVE_FOLDER, file_name))
                update_status(f"Processed and moved {file_name} to archive.")

    update_status("Parsing completed!")
    return {"message": "Parsing completed"}

if __name__ == "__main__":
    process_documents()
