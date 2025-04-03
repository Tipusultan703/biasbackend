// News Analysis Application - Complete Frontend Code

// DOM Elements
const newsText = document.getElementById("newsText");
const newsUrlInput = document.getElementById("newsUrlInput");
const newsUrl = document.getElementById("newsUrl");
const resultSection = document.getElementById("result");
const sourceResult = document.getElementById("source-result");

// Main Analysis Function
async function analyzeNews() {
    const textInput = newsText.value.trim();
    const urlInput = newsUrlInput.value.trim();

    // Validate input
    if (!textInput && !urlInput) {
        showAlert("❌ Please enter either a news article URL or text.");
        return;
    }

    let requestData = {};
    let publishedDate = "Unknown";

    // URL-based analysis
    if (urlInput) {
        if (!isValidUrl(urlInput)) {
            showAlert("❌ Please enter a valid URL (include http:// or https://)");
            return;
        }

        requestData = { url: urlInput };
        console.log("🌍 URL-based analysis requested:", urlInput);

        // Fetch published date
        publishedDate = await fetchPublishedDate(urlInput);
    } 
    // Text-based analysis
    else {
        if (textInput.length < 100) {
            showAlert("❌ Please enter at least 100 characters for analysis");
            return;
        }
        requestData = { text: textInput };
        console.log("📝 Text-based analysis requested");
    }

    try {
        showLoading(true);

        // Perform analysis
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data, publishedDate);

    } catch (error) {
        console.error("Analysis error:", error);
        showAlert(`Failed to analyze: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

async function fetchPublishedDate(url) {
    console.log("📅 Fetching published date for:", url);
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, action: 'get_date' })
        });
        
        if (!response.ok) throw new Error('Date fetch failed');
        
        const data = await response.json();
        const rawDate = data.published_date;
        
        if (!rawDate || rawDate === "Unknown") return "Publish time not available";
        
        // Return the raw date with original timezone
        return displayOriginalTime(rawDate);
        
    } catch (error) {
        console.error("Date fetch error:", error);
        return "Publish time not available";
    }
}

function displayResults(data, publishedDate) {
    // Basic info
    document.getElementById('biasScore').textContent = data.bias_score?.toFixed(1) ?? "N/A";
    document.getElementById('timestamp').innerHTML = publishedDate;  // Changed to innerHTML
    
    // Rest of the function remains the same...
    document.getElementById('originalText').innerHTML = 
        formatArticleText(data.original_article) || "No original article available.";
    // ... etc
}

// Check Source Credibility
async function checkSource() {
    const url = newsUrl.value.trim();
    if (!url) {
        showAlert("❌ Please enter a URL.");
        return;
    }

    if (!isValidUrl(url)) {
        showAlert("❌ Please enter a valid URL (include http:// or https://)");
        return;
    }

    try {
        showLoading(true, 'source');

        const response = await fetch("/api/source-check", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }

        const data = await response.json();
        displaySourceResults(data);

    } catch (error) {
        console.error("Source check error:", error);
        showAlert(`Failed to check source: ${error.message}`);
    } finally {
        showLoading(false, 'source');
    }
}

// Helper Functions

function formatArticleText(text) {
    if (!text) return null;
    return text.split('\n\n')
        .map(para => `<p>${para.replace(/\n/g, '<br>')}</p>`)
        .join('');
}

function formatRedlinedText(redlinedData) {
    if (!redlinedData || !redlinedData.biased_words?.length) {
        return "✅ No biased terms found.";
    }

    let result = "<div class='bias-results'>";
    redlinedData.biased_words.forEach((word, index) => {
        const neutral = redlinedData.neutral_alternatives?.[index] || "no alternative";
        result += `
            <div class="bias-pair">
                <span class="biased-word">❌ ${word}</span>
                <span class="neutral-word">→ ✅ ${neutral}</span>
            </div>
        `;
    });
    return result + "</div>";
}

function updateBiasVisualization(score) {
    if (!score) return;
    
    const biasMeter = document.getElementById('biasMeter');
    if (!biasMeter) return;
    
    const percentage = Math.min(100, Math.max(0, score));
    biasMeter.style.setProperty('--bias-percentage', `${percentage}%`);
    
    // Update meter color based on score
    biasMeter.className = `bias-meter ${
        score < 33 ? 'low' : 
        score < 67 ? 'medium' : 'high'
    }`;
}

function displayOriginalTime(rawDateTime) {
    if (!rawDateTime || rawDateTime === "Original publish time not available") {
        return "Publish time not available";
    }
    
    // Preserve the exact format including timezone
    const formatted = rawDateTime
        .replace('T', ' ')  // Replace T with space for readability
        .replace(/(\.\d+)?Z?$/, '');  // Remove milliseconds and Z if present
    
    return `Published: ${formatted}`;
}

function toggleView() {
    const originalText = document.getElementById("originalText");
    const rewrittenText = document.getElementById("rewrittenText");
    const toggleBtn = document.getElementById("toggleViewBtn");

    const showOriginal = originalText.style.display !== "none";
    
    originalText.style.display = showOriginal ? "none" : "block";
    rewrittenText.style.display = showOriginal ? "block" : "none";
    toggleBtn.textContent = showOriginal ? "Show Original" : "Show Rewritten";
}

function flagArticle() {
    const flagReason = prompt("Please briefly describe the issue with this analysis:");
    if (flagReason) {
        // In a real app, you would send this to your backend
        console.log("Flagged article with reason:", flagReason);
        alert("Thank you for your feedback! Our team will review this analysis.");
    }
}

function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

function showLoading(show, context = 'analysis') {
    const loader = document.querySelector(`.${context}-loader`);
    const targetElement = context === 'source' ? sourceResult : resultSection;
    
    if (show) {
        const loaderHtml = `
            <div class="${context}-loader">
                <div class="spinner"></div>
                <p>${context === 'source' ? 'Checking source...' : 'Analyzing article...'}</p>
            </div>
        `;
        targetElement.innerHTML = loaderHtml;
    } else if (loader) {
        loader.remove();
    }
}

function showAlert(message) {
    alert(message);
}

function displaySourceResults(data) {
    const credibility = data.credibility || "Unknown";
    const credibilityClass = credibility.toLowerCase();
    
    document.getElementById('sourceBiasScore').innerHTML = `
        <span class="credibility-badge ${credibilityClass}">${credibility}</span>
    `;
    sourceResult.style.display = "block";
}

// Event Listeners
document.getElementById('analyzeBtn')?.addEventListener('click', analyzeNews);
document.getElementById('sourceCheckBtn')?.addEventListener('click', checkSource);
document.getElementById('toggleViewBtn')?.addEventListener('click', toggleView);
document.getElementById('flagArticleBtn')?.addEventListener('click', flagArticle);











