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

    if (!result.flag) {
      contentContainer.innerHTML = `<p>${result.message || "Failed to load invoice."}</p>`;
      return;
    }

    const blobData = result.blob_data;

    const byteCharacters = atob(blobData);
    const byteNumbers = new Array(byteCharacters.length).fill().map((_, i) => byteCharacters.charCodeAt(i));
    const byteArray = new Uint8Array(byteNumbers);
    const pdfBlob = new Blob([byteArray], { type: 'application/pdf' });
    const pdfUrl = URL.createObjectURL(pdfBlob);

    contentContainer.innerHTML = `
      <embed src="${pdfUrl}" type="application/pdf" width="100%" height="800px" />
    `;

  } catch (error) {
    console.error("Error fetching invoice:", error);
    contentContainer.innerHTML = "<p>Error loading invoice preview.</p>";
  }
}

window.onload = loadInvoice;
