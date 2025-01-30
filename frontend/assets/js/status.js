async function checkStatus() {
    try {
      const response = await fetch("http://localhost:5000/status");
      const data = await response.json();
      const statusText = document.getElementById("status-text");
      const statusBox = document.getElementById("parsing-status");
  
      statusText.innerText = data.status;
  
      // Update status box colors based on the status
      statusBox.classList.remove("processing", "completed", "error");
      if (data.status.includes("Parsing started")) {
        statusBox.classList.add("processing");
      } else if (data.status.includes("Parsing completed")) {
        statusBox.classList.add("completed");
      } else if (data.status.includes("Error")) {
        statusBox.classList.add("error");
      }
    } catch (error) {
      console.error("Error fetching status:", error);
    }
  }
  
  // Poll the status every 3 seconds
  setInterval(checkStatus, 3000);
  