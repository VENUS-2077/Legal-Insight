from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import subprocess
import logging

app = Flask(__name__)

# Enable CORS for the frontend to access the backend
CORS(app)

# Configuration for file uploads
UPLOAD_FOLDER = 'D:/Code/Projects/Legal Insight/docs'  # Adjust the path as needed
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx'}  # Adjust extensions as needed
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
app.logger.setLevel(logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    app.logger.debug("Received file upload request.")
    
    if 'file' not in request.files:
        app.logger.error("No file part")
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        app.logger.error("No selected file")
        return jsonify({'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        app.logger.debug(f"File saved to {file_path}")

        # Trigger document parsing after the file is saved
        # Instead of calling /parse directly here, we'll queue a background task to call it
        subprocess.Popen(['python', 'D:/Code/Projects/Legal Insight/scripts/document_parser.py'])  # Adjust path if necessary
        
        return jsonify({'message': f'File {filename} uploaded successfully.'})
    else:
        app.logger.error(f"Invalid file type: {file.filename}")
        return jsonify({'message': 'Invalid file type'}), 400

@app.route('/parse', methods=['POST'])
def parse_documents():
    app.logger.debug("Starting document parsing...")

    try:
        # Start the document parsing process using subprocess
        process = subprocess.Popen(
            ['python', 'D:/Code/Projects/Legal Insight/scripts/document_parser.py'],  # Adjust path if necessary
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Capture the output and errors from the subprocess
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            app.logger.debug(f"Document parsing output: {stdout.decode()}")
            return jsonify({'message': 'Parsing started.'}), 200
        else:
            app.logger.error(f"Document parsing failed: {stderr.decode()}")
            return jsonify({'message': 'Error during parsing.'}), 500
    
    except Exception as e:
        app.logger.error(f"Error starting document parsing: {e}")
        return jsonify({'message': 'Error starting document parsing.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
