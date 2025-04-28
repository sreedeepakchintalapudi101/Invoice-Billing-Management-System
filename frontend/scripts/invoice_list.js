window.onload = function() {
    fetch("http://localhost:8081/get_ingested_invoices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: localStorage.getItem("user_id"),
        user_type: localStorage.getItem("user_type")
      })
    })
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById("invoice-tbody");
      tbody.innerHTML = "";
      if (data.flag && data.data.length > 0) {
        data.data.forEach(invoice => {
          tbody.innerHTML += `
            <tr>
              <td>${invoice.invoice_id}</td>
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
    })
    .catch(err => console.error('Error loading invoices', err));
  }
  