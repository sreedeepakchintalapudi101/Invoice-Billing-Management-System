function getParams() {
  const urlParams = new URLSearchParams(window.location.search);
  return {
    invoice_id: urlParams.get("invoice_id"),
    filename: urlParams.get("filename"),
  };
}

async function loadInvoice() {
  const { invoice_id, filename } = getParams();
  const contentContainer = document.getElementById("invoice-content");

  if (!invoice_id || !filename) {
    contentContainer.innerHTML = "<p>Missing invoice parameters.</p>";
    return;
  }

  try {
    const response = await fetch(`http://localhost:8084/get_invoice_view`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ invoice_id, filename }),
    });

    const result = await response.json();

    if (!result.flag || !Array.isArray(result.blob_datas)) {
      contentContainer.innerHTML = `<p>${result.message || "Failed to load invoice."}</p>`;
      return;
    }

    const imagesHtml = result.blob_datas.map((base64Str, idx) => {
      return `<img src="data:image/jpeg;base64,${base64Str}" alt="Page ${idx + 1}" />`;
    }).join("");

    contentContainer.innerHTML = imagesHtml;

  } catch (error) {
    console.error("Error fetching invoice:", error);
    contentContainer.innerHTML = "<p>Error loading invoice preview.</p>";
  }
}

window.onload = loadInvoice;

document.getElementById("extract-btn").addEventListener("click", function() {
  fetch("http://localhost:8085/extraction_api", {
    method: "POST",
    headers: {"content":"application/json"},
    body: JSON.stringify({invoice_id, filename})
  })
  .then(response => response.json())
  .then(data = {
    console.log("Response is:",data)
  })
  .catch(error => {
    console.log("Error", error)
  })
})