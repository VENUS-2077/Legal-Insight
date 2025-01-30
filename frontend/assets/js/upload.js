// Cached DOM elements for better performance
const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");
const progressContainer = document.querySelector(".progress-container");
const uploadProgress = document.getElementById("uploadProgress");
const uploadedCount = document.getElementById("uploadedCount");

let totalUploaded = 0; // Track total uploaded files

// Allowed file types
const allowedTypes = [
  "image/png", "image/jpeg", "image/gif",
  "application/pdf", "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain"
];

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB file size limit

// Function to validate a file
function validateFile(file) {
  if (!allowedTypes.includes(file.type)) {
    return { isValid: false, message: `Invalid file type: ${file.name}` };
  }

  if (file.size > MAX_FILE_SIZE) {
    return { isValid: false, message: `File too large: ${file.name} (Max 50MB)` };
  }

  return { isValid: true };
}

// Function to update progress bar
function updateProgress(e) {
  if (e.lengthComputable) {
    const percent = (e.loaded / e.total) * 100;
    uploadProgress.value = percent;
    console.log(`Progress: ${percent.toFixed(2)}%`);
  }
}

// Function to handle upload success
function handleSuccess(fileName) {
  totalUploaded++; // Increment uploaded file count
  uploadStatus.textContent = `Uploaded ${fileName} successfully!`;
  uploadedCount.textContent = `Total Documents Uploaded: ${totalUploaded}`;
  uploadedCount.style.display = "block";
}

// Function to handle upload failure
function handleError(fileName, errorMessage) {
  uploadStatus.textContent = `Upload Failed for ${fileName}: ${errorMessage}`;
}

// Function to upload a file
function uploadFile(file) {
  const validation = validateFile(file);
  if (!validation.isValid) {
    handleError(file.name, validation.message);
    return;
  }

  // Prepare FormData
  const formData = new FormData();
  formData.append("file", file);

  // Display upload status
  uploadStatus.textContent = `Uploading ${file.name}...`;
  progressContainer.style.display = "block";
  uploadProgress.value = 0;

  // Set up AJAX request
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "http://localhost:5000/upload", true);

  // Progress tracking
  xhr.upload.onprogress = updateProgress;

  // On load (success or failure)
  xhr.onload = function () {
    if (xhr.status === 200) {
      handleSuccess(file.name);
    } else {
      try {
        const response = JSON.parse(xhr.responseText);
        handleError(file.name, response.error || "Unknown error");
      } catch {
        handleError(file.name, "Server error. Please try again.");
      }
    }
  };

  // Handle network errors
  xhr.onerror = function () {
    handleError(file.name, "Network error. Please check your connection and try again.");
  };

  // Send file to server
  xhr.send(formData);
}

// Function to handle file input change
fileInput.addEventListener("change", function (event) {
  const files = event.target.files; // Get all selected files
  if (files.length === 0) return;

  // Reset progress bar and count display
  progressContainer.style.display = "none";
  uploadedCount.style.display = "none";

  Array.from(files).forEach(uploadFile); // Upload each file one by one
  fileInput.value = ""; // Reset file input field after selection
});

// Function to trigger the upload process
function uploadFiles() {
  const files = fileInput.files;
  if (files.length === 0) {
    uploadStatus.textContent = "Please select files first.";
    return;
  }

  // Upload selected files
  Array.from(files).forEach(uploadFile);
  fileInput.value = ""; // Reset file input field after selection
}
