// Cached DOM elements
const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");
const progressContainer = document.querySelector(".progress-container");
const uploadProgress = document.getElementById("uploadProgress");
const uploadedCount = document.getElementById("uploadedCount");
const statusBox = document.getElementById("parsing-status");
const statusText = document.getElementById("status-text");

let totalUploaded = 0;

// Function to upload a file
function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  uploadStatus.textContent = `Uploading ${file.name}...`;
  progressContainer.style.display = "block";
  uploadProgress.value = 0;

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "http://localhost:5000/upload", true);

  // Track upload progress
  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable) {
      uploadProgress.value = (e.loaded / e.total) * 100;
    }
  };

  // Handle response after upload
  xhr.onload = function () {
    if (xhr.status === 200) {
      const response = JSON.parse(xhr.responseText);
      uploadStatus.textContent = response.message;
      totalUploaded++;
      uploadedCount.textContent = `Total Documents Uploaded: ${totalUploaded}`;
      uploadedCount.style.display = "block";

      // Automatically start document parsing
      startParsing();
    } else {
      // Handle error from backend
      uploadStatus.textContent = `Upload failed with status: ${xhr.status}`;
    }
  };

  // Handle network error
  xhr.onerror = function () {
    uploadStatus.textContent = "Network error! Please try again. The server might be down.";
    console.error("Network error:", xhr.status, xhr.statusText);
  };

  // Send the file to backend
  xhr.send(formData);
}

// Function to start document parsing
function startParsing() {
  statusBox.classList.add("processing");
  statusText.textContent = "Reading documents...";

  // Call the parsing endpoint
  fetch("http://localhost:5000/parse", { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      statusText.textContent = "Parsing Completed!";
      statusBox.classList.remove("processing");
      statusBox.classList.add("completed");
      console.log(data);
    })
    .catch((error) => {
      statusText.textContent = "Error parsing documents!";
      statusBox.classList.remove("processing");
      statusBox.classList.add("error");
      console.error("Parsing error:", error);
    });
}

// Handle file input change
fileInput.addEventListener("change", function (event) {
  const files = event.target.files;
  if (files.length === 0) return;

  // Upload each file
  Array.from(files).forEach(uploadFile);
  fileInput.value = "";  // Reset file input after selection
});
