function analyzeNews() {
    console.log("🔍 Debug: analyzeNews() function started!");

    // Get user input from the text box
    const text = document.getElementById("newsText").value.trim();
    if (!text) {
        console.log("⚠️ Debug: No text input found.");
        alert("❌ Please enter news text.");
        return;
    }

    // API call to analyze the news text for bias
    fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("✅ Debug: Data from Backend:", data);

        // Process and display the bias score
        const biasScore = parseFloat(data.bias_score);
        document.getElementById("biasScore").innerText = isNaN(biasScore) 
            ? "Bias Score: Not Available" 
            : `Bias Score: ${biasScore.toFixed(2)}`;

        // Process and display redlined text
        const redlinedArray = Array.isArray(data.redlined_text) 
            ? data.redlined_text 
            : ["✅ No biased terms found."];
        const redlinedHtml = redlinedArray.map(change => {
            if (change.includes("Biased words:")) {
                return `<span style="color: red;">❌ ${change}</span>`;
            } else if (change.includes("Neutral alternatives:")) {
                return `<span style="color: green;">✅ ${change}</span>`;
            }
            return change;
        }).join("<br>");
        document.getElementById("redlinedText").innerHTML = redlinedHtml;

        // Display rewritten text if available
        const rewrittenText = data.rewritten || "No rewritten text available.";
        document.getElementById("rewrittenText").innerText = rewrittenText;

        // Update chart or visualization for bias score (if applicable)
        updateBiasChart(biasScore);

        // Show results section
        document.getElementById("result").style.display = "block";
    })
    .catch(error => {
        console.error("❌ Error analyzing news:", error);
        alert(`Failed to analyze text. Error: ${error.message}`);
    });
}

function checkSource() {
    console.log("📡 Debug: checkSource() function started!");

    // Get user input for source URL
    const url = document.getElementById("newsUrl").value.trim();
    if (!url) {
        alert("❌ Please enter a URL.");
        return;
    }

    console.log("📡 Debug: Checking source credibility for URL:", url);

    // API call to check the credibility of the URL source
    fetch("http://127.0.0.1:5000/source_check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("✅ Debug: Source Check API Response:", data);

        // Display the source credibility score
        const credibilityText = data.credibility || "Unknown";
        document.getElementById("sourceBiasScore").innerText = `Credibility: ${credibilityText}`;

        // Show the source result section
        document.getElementById("source-result").style.display = "block";
    })
    .catch(error => {
        console.error("❌ Error checking source:", error);
        alert(`Failed to check source. Error: ${error.message}`);
    });
}

function toggleView() {
    const original = document.getElementById("originalText");
    const rewritten = document.getElementById("rewrittenText");

    if (original.style.display === "none") {
        original.style.display = "block";
        rewritten.style.display = "none";
    } else {
        original.style.display = "none";
        rewritten.style.display = "block";
    }
}

function flagArticle() {
    alert("🚩 Article flagged for review.");
}


// Helper function to update the bias score chart (placeholder)
function updateBiasChart(biasScore) {
    console.log(`📊 Updating chart with Bias Score: ${biasScore}`);
    // Placeholder for chart integration logic
}













