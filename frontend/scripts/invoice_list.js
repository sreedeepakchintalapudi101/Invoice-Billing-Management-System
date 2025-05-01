document.addEventListener("DOMContentLoaded", async () => {
  const user_id = localStorage.getItem("user_id");
  const user_type = localStorage.getItem("user_type");

  const tbody = document.getElementById("invoice-tbody");

  try {
    const response = await fetch("http://localhost:8084/get_ingested_invoices", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ user_id, user_type })
    });

    const data = await response.json();
    tbody.innerHTML = "";

    if (data.flag && Array.isArray(data.data) && data.data.length > 0) {
      data.data.forEach(invoice => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${invoice.invoice_id}</td>
          <td>${invoice.file_name}</td>
          <td>${invoice.ingested_datetime}</td>
          <td>${invoice.from_email || 'N/A'}</td>
        `;

        row.style.cursor = "pointer";
        row.addEventListener("click", () => {
          const invoiceId = encodeURIComponent(invoice.invoice_id);
          const fileName = encodeURIComponent(invoice.file_name);
          window.location.href = `invoice_preview.html?invoice_id=${invoiceId}&filename=${fileName}`;
        });

        tbody.appendChild(row);
      });
    } else {
      tbody.innerHTML = `
        <tr><td colspan="4" style="text-align:center;">No Invoices Found</td></tr>
      `;
    }
  } catch (error) {
    console.error("Error occurred while fetching invoices:", error);
    tbody.innerHTML = `
      <tr><td colspan="4" style="text-align:center;">Failed to load invoices</td></tr>
    `;
  }
});
