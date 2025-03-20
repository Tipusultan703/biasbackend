// Analyze news for bias
function analyzeNews() {
    console.log("🔍 Debug: analyzeNews() function started!");

    const text = document.getElementById("newsText")?.value.trim();
    if (!text) {
        console.warn("⚠️ Debug: No text input found.");
        alert("❌ Please enter news text.");
        return;
    }

    fetch("https://biasbackend.onrender.com/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
    })
    .then(response => response.ok ? response.json() : Promise.reject(`Server error: ${response.status}`))
    .then(data => {
        console.log("✅ Debug: Data from Backend:", data);

        const biasScore = parseFloat(data.bias_score);
        const biasScoreElem = document.getElementById("biasScore");
        if (biasScoreElem) {
            biasScoreElem.innerText = isNaN(biasScore) 
                ? "Bias Score: Not Available" 
                : `Bias Score: ${biasScore.toFixed(2)}`;
        }

        document.getElementById("originalText").innerText = text;
        document.getElementById("redlinedText").innerHTML = formatRedlinedText(data.redlined_text);
        document.getElementById("rewrittenText").innerText = data.rewritten || "No rewritten text available.";

        document.getElementById("rewrittenText").style.display = "none"; // Ensure hidden initially
        document.getElementById("result").style.display = "block";

        updateBiasChart(biasScore);
    })
    .catch(error => {
        console.error("❌ Error analyzing news:", error);
        alert(`Failed to analyze text. Error: ${error}`);
    });
}

// Format redlined text for display
function formatRedlinedText(redlinedData) {
    if (!redlinedData?.biased_words?.length) {
        return "✅ No biased terms found.";
    }

    const biasedWords = redlinedData.biased_words.map(word => `<span style="color: red;">❌ ${word}</span>`).join(", ");
    const neutralAlternatives = redlinedData.neutral_alternatives.map(word => `<span style="color: green;">✅ ${word}</span>`).join(", ");

    return `<strong>Biased Words:</strong> ${biasedWords}<br><strong>Neutral Alternatives:</strong> ${neutralAlternatives}`;
}

// Check source credibility
function checkSource() {
    console.log("📡 Debug: checkSource() function started!");

    const url = document.getElementById("newsUrl")?.value.trim();
    if (!url) {
        alert("❌ Please enter a URL.");
        return;
    }

    fetch("https://biasbackend.onrender.com/api/source-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
    })
    .then(response => response.ok ? response.json() : Promise.reject(`Server error: ${response.status}`))
    .then(data => {
        console.log("✅ Debug: Source Check API Response:", data);
        const sourceBiasElem = document.getElementById("sourceBiasScore");
        const sourceResultElem = document.getElementById("source-result");
        if (sourceBiasElem) {
            sourceBiasElem.innerText = `Credibility: ${data.credibility || "Unknown"}`;
            if (sourceResultElem) sourceResultElem.style.display = "block";
        }
    })
    .catch(error => {
        console.error("❌ Error checking source:", error);
        alert(`Failed to check source. Error: ${error}`);
    });
}

// Toggle between original and rewritten text
function toggleView() {
    const original = document.getElementById("originalText");
    const rewritten = document.getElementById("rewrittenText");

    if (!original || !rewritten) {
        console.error("❌ Error: Elements not found for toggle view.");
        return;
    }

    if (rewritten.style.display === "none" || rewritten.style.display === "") {
        rewritten.style.display = "block";
        original.style.display = "none";
    } else {
        rewritten.style.display = "none";
        original.style.display = "block";
    }
}

// Flag article for review
function flagArticle() {
    alert("🚩 Article flagged for review.");
}

// Update the bias score chart (placeholder)
function updateBiasChart(biasScore) {
    console.log(`📊 Updating chart with Bias Score: ${biasScore}`);
}










