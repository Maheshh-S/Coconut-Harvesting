function setupDetection(endpoint) {
  const form = document.getElementById("uploadForm");
  const fileInput = document.getElementById("fileInput");
  const uploadArea = document.getElementById("uploadArea");
  const detectBtn = document.getElementById("detectBtn");
  const previewImg = document.getElementById("previewImg");
  const outputImg = document.getElementById("outputImg");
  const jsonOutput = document.getElementById("jsonOutput");
  const originalPlaceholder = document.getElementById("originalPlaceholder");
  const resultPlaceholder = document.getElementById("resultPlaceholder");
  const dataPlaceholder = document.getElementById("dataPlaceholder");

  // Handle drag and drop events
  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = "#5ac8fa";
    uploadArea.style.transform = "scale(1.02)";
  });

  uploadArea.addEventListener("dragleave", () => {
    uploadArea.style.borderColor = "#4cd964";
    uploadArea.style.transform = "scale(1)";
  });

  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = "#4cd964";
    uploadArea.style.transform = "scale(1)";
    
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      handleFileSelection();
    }
  });

  fileInput.addEventListener("change", handleFileSelection);

  function handleFileSelection() {
    const file = fileInput.files[0];
    if (file) {
      // Show preview image
      previewImg.src = URL.createObjectURL(file);
      previewImg.style.display = "block";
      originalPlaceholder.style.display = "none";
      
      // Reset results
      outputImg.style.display = "none";
      resultPlaceholder.style.display = "block";
      jsonOutput.style.display = "none";
      dataPlaceholder.style.display = "block";
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) {
      alert("Please select an image first");
      return;
    }

    // Show loading state
    detectBtn.disabled = true;
    detectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    outputImg.style.display = "none";
    resultPlaceholder.innerHTML = '<i class="fas fa-spinner fa-spin"></i><p>Analyzing image...</p>';
    resultPlaceholder.style.display = "block";
    jsonOutput.style.display = "none";
    dataPlaceholder.innerHTML = '<i class="fas fa-spinner fa-spin"></i><p>Processing detection data...</p>';
    dataPlaceholder.style.display = "block";

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(endpoint, { method: "POST", body: formData });
      const data = await res.json();

      if (data.output_image) {
        // Show detection result
        outputImg.src = data.output_image;
        outputImg.style.display = "block";
        resultPlaceholder.style.display = "none";
        
        // Show JSON data
        jsonOutput.textContent = JSON.stringify(data.predictions, null, 2);
        jsonOutput.style.display = "block";
        dataPlaceholder.style.display = "none";
      } else {
        // Handle error response
        jsonOutput.textContent = JSON.stringify(data, null, 2);
        jsonOutput.style.display = "block";
        dataPlaceholder.style.display = "none";
        resultPlaceholder.innerHTML = '<i class="fas fa-exclamation-triangle"></i><p>Error processing image</p>';
      }
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while processing the image");
      resultPlaceholder.innerHTML = '<i class="fas fa-exclamation-triangle"></i><p>Error processing image</p>';
      dataPlaceholder.innerHTML = '<i class="fas fa-exclamation-triangle"></i><p>Error processing detection data</p>';
    } finally {
      // Reset button state
      detectBtn.disabled = false;
      detectBtn.innerHTML = '<i class="fas fa-search"></i> Detect Trees';
    }
  });
}