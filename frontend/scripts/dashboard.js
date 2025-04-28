function showTab(tabName) {
    document.querySelectorAll('.tab-section').forEach(tab => {
      tab.classList.remove('active');
    });
    document.getElementById(tabName + '-tab').classList.add('active');
  
    if (tabName === 'files') {
      loadIngestedFiles();
    }
  }
  
  function loadIngestedFiles() {
    fetch("http://localhost:8081/get_ingested_files", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: localStorage.getItem("user_id"),
        user_type: localStorage.getItem("user_type")
      })
    })
    .then(res => res.json())
    .then(data => {
      const tbody = document.getElementById("files-tbody");
      tbody.innerHTML = "";
      data.data.forEach(file => {
        tbody.innerHTML += `
          <tr>
            <td>${file.file_name}</td>
            <td>${file.file_type}</td>
            <td>${file.status}</td>
            <td>${file.upload_time}</td>
          </tr>
        `;
      });
    })
    .catch(error => {
      console.error('Error fetching ingested files:', error);
    });
  }
  