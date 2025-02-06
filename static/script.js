document.addEventListener("DOMContentLoaded", () => {
    let loading = false;
    let queue = ["Python_(programming_language)"];

    async function fetchArticle(topic) {
        if (loading) return;
        loading = true;

        const response = await fetch(`/get_article?topic=${topic}`);
        const data = await response.json();
        
        if (data.error) {
            console.error("Error loading article:", data.error);
            return;
        }

        const contentDiv = document.getElementById("content");

        let articleDiv = document.createElement("div");
        articleDiv.classList.add("article");
        articleDiv.innerHTML = `<h2>${data.title}</h2><p>${data.extract}</p>`;
        contentDiv.appendChild(articleDiv);

        data.links.forEach(link => {
            let linkBtn = document.createElement("button");
            linkBtn.innerText = link;
            linkBtn.classList.add("wiki-link");
            linkBtn.onclick = () => queue.push(link.replace(/ /g, "_"));
            contentDiv.appendChild(linkBtn);
        });

        loading = false;
    }

    window.addEventListener("scroll", () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            if (queue.length > 0) fetchArticle(queue.shift());
        }
    });

    fetchArticle(queue.shift());
});
