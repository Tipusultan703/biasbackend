# frontend/static/chrome_extension.js
document.addEventListener("DOMContentLoaded", function () {
    let paragraphs = document.getElementsByTagName("p");
    for (let p of paragraphs) {
        let originalText = p.innerText;
        fetch("http://127.0.0.1:5000/api/rewrite", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: originalText })
        })
        .then(response => response.json())
        .then(data => {
            if (data.rewritten) {
                p.innerHTML = `<span style="background-color: yellow;">${data.rewritten}</span>`;
            }
        })
        .catch(error => console.error("Error rewriting text:", error));
    }
});