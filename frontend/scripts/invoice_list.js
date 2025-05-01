document.addEventListener("DOMContentLoaded", async () => {
  const user_id = localStorage.getItem("user_id");
  const user_type = localStorage.getItem("user_type");  // Fixed typo

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
        tbody.innerHTML += `
          <tr>
            <td>${invoice.invoice_id}</td>
            <td>${invoice.file_name}</td>
            <td>${invoice.ingested_datetime}</td>
            <td>${invoice.ingested_from}</td>
          </tr>
        `;
      });
    } else {
      tbody.innerHTML = `
        <tr><td colspan="3" style="text-align:center;">No Invoices Found</td></tr>
      `;
    }
  } catch (error) {
    console.error("Error occurred with Exception", error);
    tbody.innerHTML = `
      <tr><td colspan="3" style="text-align:center;">Failed to load invoices</td></tr>
    `;
  }
});
