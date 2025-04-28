function showTab(tabName) {
    document.querySelectorAll('.tab-section').forEach(tab => {
      tab.classList.add('hidden');
    });
  
    document.getElementById(tabName + '-tab').classList.remove('hidden');
  }
  
  // Show Dashboard tab by default
  window.onload = function() {
    showTab('dashboard');
  };
  