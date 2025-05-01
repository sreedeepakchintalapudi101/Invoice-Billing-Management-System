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
      const response = await fetch(`/get_invoice_view/${invoice_id}/${filename}`);
      if (!response.ok) throw new Error("Failed to load invoice");
      
      const content = await response.text();
      contentContainer.innerHTML = content;
    } catch (error) {
      console.error("Error fetching invoice:", error);
      contentContainer.innerHTML = "<p>Error loading invoice preview.</p>";
    }
  }
  
  window.onload = loadInvoice;
  