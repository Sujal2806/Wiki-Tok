document.addEventListener("DOMContentLoaded", () => {
    let tabCount = 0;

    document.getElementById("searchBtn").addEventListener("click", function () {
        const topic = document.getElementById("searchInput").value.trim();
        if (topic) {
            fetchArticle(topic.replace(/ /g, "_"));
        }
    });
});

async function fetchArticle(topic) {
    try {
        const response = await fetch(`/get_article?topic=${encodeURIComponent(topic)}`);
        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        addTab(data.title, data.extract, data.page_url);
    } catch (error) {
        console.error("Failed to fetch article:", error);
        alert("Failed to load article. Check console.");
    }
}

function addTab(title, extract, url) {
    tabCount++;
    const tabId = `tab${tabCount}`;
    const articleTabs = document.getElementById("articleTabs");
    const articleContent = document.getElementById("articleContent");

    // Add new tab
    let newTab = document.createElement("li");
    newTab.classList.add("nav-item");
    newTab.innerHTML = `
        <button class="nav-link ${tabCount === 1 ? 'active' : ''}" data-bs-toggle="tab" data-bs-target="#${tabId}">${title}</button>
    `;
    articleTabs.appendChild(newTab);

    // Add content for the tab
    let tabPane = document.createElement("div");
    tabPane.classList.add("tab-pane", "fade", tabCount === 1 ? "show", "active" : "");
    tabPane.id = tabId;
    tabPane.innerHTML = `
        <div class="p-3">
            <h2><a href="${url}" target="_blank">${title}</a></h2>
            <p>${extract}</p>
        </div>
    `;
    articleContent.appendChild(tabPane);
}
