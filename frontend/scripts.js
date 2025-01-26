document.getElementById("upload-form").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById("file-input");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
  
    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
  
      if (response.ok) {
        const result = await response.json();
        document.getElementById("results").innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
      } else {
        alert("Failed to upload document");
      }
    } catch (error) {
      alert("Error uploading document: " + error);
    }
  });
  