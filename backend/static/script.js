// ✅ Analyze News for Bias
function analyzeNews() {
    console.log("🔍 Debug: analyzeNews() function started!");

    const inputText = document.getElementById('newsText').value;

    if (!inputText) {
        alert("❌ Please enter some text to analyze.");
        return;
    }

    fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText }),
    })
    .then(response => {
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log("✅ Debug: Data from Backend:", data);

        document.getElementById('biasScore').textContent = data.bias_score ?? "Error";
        document.getElementById('originalText').textContent = inputText;
        document.getElementById('rewrittenText').textContent = data.rewritten ?? "No rewritten text available";
        document.getElementById('redlinedText').innerHTML = formatRedlinedText(data.redlined_text);

        document.getElementById('result').style.display = 'block';
    })
    .catch(error => {
        console.error("❌ Error analyzing news:", error);
        alert(`Failed to analyze text. ${error.message}`);
    });
}

// ✅ Format redlined text for display
function formatRedlinedText(redlinedData) {
    if (!redlinedData?.biased_words?.length) {
        return "✅ No biased terms found.";
    }

    const biasedWords = redlinedData.biased_words.map(word => `<span style="color: red;">❌ ${word}</span>`).join(", ");
    const neutralAlternatives = redlinedData.neutral_alternatives.map(word => `<span style="color: green;">✅ ${word}</span>`).join(", ");

    return `<strong>Biased Words:</strong> ${biasedWords}<br><strong>Neutral Alternatives:</strong> ${neutralAlternatives}`;
}

// ✅ Check Source Credibility
function checkSource() {
    console.log("📡 Debug: checkSource() function started!");

    const url = document.getElementById("newsUrl")?.value.trim();
    if (!url) {
        alert("❌ Please enter a URL.");
        return;
    }

    fetch("/api/source-check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
    })
    .then(response => {
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log("✅ Debug: Source Check API Response:", data);
        const sourceBiasElem = document.getElementById("sourceBiasScore");
        const sourceResultElem = document.getElementById("source-result");

        if (sourceBiasElem) {
            sourceBiasElem.innerText = `Credibility: ${data.credibility || "Unknown"}`;
            sourceResultElem.style.display = "block";
        }
    })
    .catch(error => {
        console.error("❌ Error checking source:", error);
        alert(`Failed to check source. Error: ${error}`);
    });
}

// ✅ Toggle between Original and Rewritten Text
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

// ✅ Flag Article for Review
function flagArticle() {
    alert("🚩 Article flagged for review.");
}

// ✅ Update Bias Score Chart (Placeholder for future implementation)
function updateBiasChart(biasScore) {
    console.log(`📊 Updating chart with Bias Score: ${biasScore}`);
}











