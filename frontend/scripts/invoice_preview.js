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

document.getElementById("extract-btn").addEventListener("click", function () {
  const { invoice_id, filename } = getParams();

  fetch("http://localhost:8085/convert_image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ invoice_id, filename })
  })
    .then(response => response.json())
    .then(data => {
      console.log("Response is:", data);
      const container = document.getElementById("extracted-values")
      if(!data || !data.extracted_dict || data.extracted_dict.length === 0 || Object.keys(data.extracted_dict).length === 0)
      {
        container.innerHTML = "<h2>No Data is extracted!</h2>";
        return;
      }
      else {
        let html = "<h2>Extracted Invoice Data:</h2><table border='1' cellpadding='8' cellspacing='0'>";
        for ([key, value] of Object.entries(data.extracted_dict)) {
          html += "<tr><td><strong>${key}</strong></td><td>${value}</td></tr>"
        }
        html += "</table>";
        container.innerHTML = html;
      }
    })
    .catch(error => {
      console.error("Error:", error);
      document.getElementById("extracted-values").innerHTML = "<h2>Error in loading extracted data</h2>"
    });
});

document.getElementById("")