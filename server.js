const express = require('express');
const multer = require('multer');
const path = require('path');

// Initialize Express app
const app = express();
const port = 5000;

// Set up multer storage (save files to D:/Code/Projects/Legal Insight/docs)
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'D:/Code/Projects/Legal Insight/docs');  // Directory to save files
  },
  filename: (req, file, cb) => {
    const fileExtension = path.extname(file.originalname);
    const fileName = Date.now() + fileExtension;  // Unique file name based on timestamp
    cb(null, fileName);
  }
});

// Initialize multer upload middleware
const upload = multer({ storage: storage });

// Handle the POST request for file upload
app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded');
  }

  res.send('File uploaded successfully');
});

// Start the server
app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
