async function checkStatus() {
  try {
    const response = await fetch("http://localhost:5000/status");
    const data = await response.json();
    const statusText = document.getElementById("status-text");
    const statusBox = document.getElementById("parsing-status");

    // Delay status update for smoother transition
    setTimeout(() => {
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
    }, 500);  // Delay before applying the new status (500ms)

  } catch (error) {
    console.error("Error fetching status:", error);
  }
}

// Poll the status every 3 seconds with delay in updating status
setInterval(checkStatus, 3000);  // 3 seconds interval between status checks
