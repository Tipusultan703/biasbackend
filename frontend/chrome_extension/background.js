chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: analyzePage
    });
});

function analyzePage() {
    let selectedText = window.getSelection().toString().trim();
    
    if (!selectedText) {
        alert("❌ No text selected. Please highlight some text.");
        return;
    }

    console.log("🔍 Sending text to backend for analysis...");

    fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: selectedText })
    })
    .then(response => response.json())
    .then(data => {
        alert(`✅ Bias Score: ${data.bias_score}\nRewritten Text: ${data.rewritten}`);
        console.log("✅ API Response:", data);
    })
    .catch(error => {
        console.error("❌ API Fetch Error:", error);
        alert("❌ Error analyzing text. Try again.");
    });
}



