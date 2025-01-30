import os
import json
import shutil
import time
from pathlib import Path
from pdfminer.high_level import extract_text
from docx import Document

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

def extract_text_from_file(file_path):
    """Extract text from various document types."""
    file_ext = Path(file_path).suffix.lower()

    if file_ext == ".pdf":
        return extract_text(file_path)
    elif file_ext == ".docx":
        return extract_text_from_docx(file_path)
    elif file_ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return None  # Unsupported file type

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

def process_documents():
    """Process all documents in the docs folder and save extracted text."""
    update_status("Parsing started...")

    for file_name in os.listdir(DOCS_FOLDER):
        file_path = os.path.join(DOCS_FOLDER, file_name)

        if os.path.isfile(file_path):
            extracted_text = extract_text_from_file(file_path)

            if extracted_text is not None:
                output_path = os.path.join(PROCESSED_FOLDER, f"{Path(file_name).stem}.json")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump({"filename": file_name, "content": extracted_text}, f, ensure_ascii=False, indent=4)

                # Move the file after processing with error handling
                try:
                    shutil.move(file_path, os.path.join(ARCHIVE_FOLDER, file_name))
                    update_status(f"Moved file {file_name} to archive.")
                except Exception as e:
                    update_status(f"Error moving {file_name}: {str(e)}")

    update_status("Parsing completed!")
    return {"message": "Parsing completed"}

if __name__ == "__main__":
    process_documents()
