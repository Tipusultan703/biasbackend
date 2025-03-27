document.addEventListener('DOMContentLoaded', () => {
  // Check if text is selected using right-click (context menu)
  chrome.storage.local.get('selectedText', (data) => {
    if (data.selectedText) {
      analyzeText(data.selectedText);
      chrome.storage.local.remove('selectedText'); // Clear after use
    } else {
      // If no context menu text, check directly for selected text
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          func: () => window.getSelection().toString()
        }, (results) => {
          if (chrome.runtime.lastError) {
            console.error("❌ Error:", chrome.runtime.lastError.message);
            return;
          }

          const selectedText = results?.[0]?.result?.trim();

          if (selectedText) {
            analyzeText(selectedText);
          } else {
            alert("❌ Please select some text before clicking the extension.");
          }
        });
      });
    }
  });

  // Analyze the text and display results
  function analyzeText(text) {
    fetch("https://biasbackend.onrender.com/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    })
    .then(response => {
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      return response.json();
    })
    .then(data => {
      document.getElementById('bias-score').textContent = data.bias_score ?? "Error";
      document.getElementById('original-text').textContent = text;
      document.getElementById('rewritten-text').textContent = data.rewritten ?? "No rewritten text available";
      document.getElementById('result').style.display = "block";
    })
    .catch(error => {
      console.error("❌ API Error:", error);
      alert("❌ Failed to analyze text. Try again.");
    });
  }

  document.getElementById('closeButton').addEventListener('click', () => {
    window.close();
  });
});




