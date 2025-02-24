// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const feedContainer = document.querySelector('.feed-container');
    const tagButtons = document.querySelectorAll('.tag-btn');
    const articleTemplate = document.getElementById('article-template');
    
    let currentTag = 'trending';
    let currentPage = 1;
    let loading = false;
    let hasMore = true;
    
    // Initial load
    loadArticles();
    
    // Handle tag selection
    tagButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tag = this.getAttribute('data-tag');
            
            // Don't reload if same tag is clicked
            if (tag === currentTag) return;
            
            // Update active tag
            tagButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Reset and load new content
            currentTag = tag;
            currentPage = 1;
            hasMore = true;
            feedContainer.innerHTML = '<div class="loader">Loading...</div>';
            loadArticles();
        });
    });
    
    // Infinite scroll
    window.addEventListener('scroll', function() {
        if (loading || !hasMore) return;
        
        // Check if we've scrolled to the bottom
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
            currentPage++;
            loadArticles();
        }
    });
    
    function loadArticles() {
        if (loading || !hasMore) return;
        
        loading = true;
        console.log(`Loading ${currentTag} articles, page ${currentPage}`);
        
        // Show loader if first page
        if (currentPage === 1) {
            feedContainer.innerHTML = '<div class="loader">Loading...</div>';
        } else {
            // Add loader at the bottom for additional pages
            const loader = document.createElement('div');
            loader.className = 'loader';
            loader.textContent = 'Loading more...';
            feedContainer.appendChild(loader);
        }
        
        // Determine endpoint
        let url;
        if (currentTag === 'trending') {
            url = `/api/trending?page=${currentPage}`;
        } else {
            url = `/api/tags/${currentTag}?page=${currentPage}`;
        }
        
        console.log(`Fetching from: ${url}`);
        
        // Fetch articles
        fetch(url)
            .then(response => {
                console.log(`Response status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                console.log('Data received:', data);
                
                // Remove loader
                const loaders = document.querySelectorAll('.loader');
                loaders.forEach(loader => loader.remove());
                
                // Update has more flag
                hasMore = data.has_more;
                
                // Process articles
                const articles = data.topics || data.articles;
                console.log(`Found ${articles ? articles.length : 0} articles`);
                
                if (!articles || articles.length === 0) {
                    if (currentPage === 1) {
                        feedContainer.innerHTML = '<div class="no-results">No articles found. Try another tag or refresh the page.</div>';
                    }
                    return;
                }
                
                // Clear container on first page
                if (currentPage === 1) {
                    feedContainer.innerHTML = '';
                }
                
                // Add articles to feed
                articles.forEach(article => {
                    const clone = document.importNode(articleTemplate.content, true);
                    
                    // Set content
                    clone.querySelector('.article-title').textContent = article.title;
                    clone.querySelector('.article-summary').textContent = article.summary;
                    clone.querySelector('.read-more').href = article.url;
                    
                    // Set image
                    const img = clone.querySelector('.article-image img');
                    img.src = article.image_url || 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/200px-Wikipedia-logo-v2.svg.png';
                    img.alt = article.title;
                    
                    feedContainer.appendChild(clone);
                });
            })
            .catch(error => {
                console.error('Error fetching articles:', error);
                feedContainer.innerHTML = '<div class="error">Error loading content. Please try again.</div>';
            })
            .finally(() => {
                loading = false;
            });
    }
});