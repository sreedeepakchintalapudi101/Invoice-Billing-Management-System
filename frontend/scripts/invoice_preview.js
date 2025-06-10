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
    const response = await fetch("http://localhost:8084/get_invoice_view", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ invoice_id, filename }),
    });

    const result = await response.json();

    if (!result.flag || !Array.isArray(result.blob_datas)) {
      contentContainer.innerHTML = `<p>${result.message || "Failed to load invoice."}</p>`;
      return;
    }

    const imagesHtml = result.blob_datas
      .map(
        (base64Str, idx) =>
          `<img src="data:image/jpeg;base64,${base64Str}" alt="Page ${idx + 1}" />`
      )
      .join("");

    contentContainer.innerHTML = imagesHtml;
  } catch (error) {
    console.error("Error fetching invoice:", error);
    contentContainer.innerHTML = "<p>Error loading invoice preview.</p>";
  }
}

function showTab(tabId) {
  // Hide all tab contents
  document.querySelectorAll(".tab-content").forEach((tab) => {
    tab.classList.remove("active");
  });

  // Remove active class from all buttons
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.remove("active");
  });

  // Show selected tab and activate its button
  document.getElementById(tabId).classList.add("active");

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    if (btn.getAttribute("onclick")?.includes(tabId)) {
      btn.classList.add("active");
    }
  });
}

window.onload = loadInvoice;

document.getElementById("extract-btn").addEventListener("click", function () {
  const { invoice_id, filename } = getParams();

  fetch("http://localhost:8085/convert_image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ invoice_id, filename }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Response is:", data);

      const extracted_values_container = document.getElementById("extracted-values");
      const table_values_container = document.getElementById("table-tab");

      // Clear both containers first
      extracted_values_container.innerHTML = "";
      table_values_container.innerHTML = "";

      // Extracted values
      if (!data || !data.extracted_dict || Object.keys(data.extracted_dict).length === 0) {
        extracted_values_container.innerHTML = "<h2>No Data is extracted!</h2>";
      } else {
        let extracted_html = "<div class='box-container'>";
        for (const [key, value] of Object.entries(data.extracted_dict)) {
          extracted_html += `
            <div class='data-box'>
              <h2 class='box-key'>${key}</h2>
              <p class='data-value'>${value}</p>
            </div>
          `;
        }
        extracted_html += "</div>";
        extracted_values_container.innerHTML = extracted_html;
      }

      // Tables
      if (!data || !data.html_table) {
        table_values_container.innerHTML = "<h2>No Tables are Extracted</h2>";
      } else {
        table_values_container.innerHTML = data.html_table;
        showTab("table-tab");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      document.getElementById("extracted-values").innerHTML = "<h2>No data is extracted</h2>";
    })
})