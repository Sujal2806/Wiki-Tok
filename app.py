# app.py
from flask import Flask, render_template, jsonify, request
import requests
import random
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# Cache for trending topics to avoid repeated API calls
trending_cache = {}
topic_articles_cache = {}

def get_trending_topics():
    """Get trending topics from Wikipedia"""
    if 'topics' in trending_cache and trending_cache['topics']:
        return trending_cache['topics']
    
    try:
        # Alternative method: get articles from Wikipedia's current events portal
        response = requests.get('https://en.wikipedia.org/wiki/Portal:Current_events')
        soup = BeautifulSoup(response.text, 'html.parser')
        
        topics = []
        # Find recent events content
        content_div = soup.find('div', {'class': 'current-events-content vevent'})
        
        if content_div:
            links = content_div.find_all('a', href=True)
            for i, link in enumerate(links[:20]):  # Limit to 20 topics
                # Filter out non-article links
                if '/wiki/' in link.get('href') and ':' not in link.get('href'):
                    title = link.get('title') or link.text
                    url = 'https://en.wikipedia.org' + link.get('href')
                    
                    # Avoid duplicates
                    if any(t['title'] == title for t in topics):
                        continue
                        
                    topics.append({
                        'title': title,
                        'url': url
                    })
                    
                    if len(topics) >= 15:  # Ensure we don't get too many
                        break
        
        # If we couldn't get topics from Current Events, fall back to featured articles
        if not topics:
            response = requests.get('https://en.wikipedia.org/wiki/Wikipedia:Featured_articles')
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find featured article links
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if content_div:
                links = content_div.find_all('a', href=True)
                for link in links[:30]:  # Check more links since we'll filter many out
                    if '/wiki/' in link.get('href') and ':' not in link.get('href'):
                        title = link.get('title') or link.text
                        if not title or len(title) < 3:  # Skip very short titles
                            continue
                            
                        url = 'https://en.wikipedia.org' + link.get('href')
                        
                        # Avoid duplicates
                        if any(t['title'] == title for t in topics):
                            continue
                            
                        topics.append({
                            'title': title,
                            'url': url
                        })
                        
                        if len(topics) >= 15:  # Limit to 15 topics
                            break
        
        # Cache results if we found any
        if topics:
            trending_cache['topics'] = topics
            
        return topics
    except Exception as e:
        print(f"Error fetching trending topics: {e}")
        # Return some hardcoded topics as fallback
        return [
            {'title': 'Artificial Intelligence', 'url': 'https://en.wikipedia.org/wiki/Artificial_intelligence'},
            {'title': 'Climate Change', 'url': 'https://en.wikipedia.org/wiki/Climate_change'},
            {'title': 'Solar System', 'url': 'https://en.wikipedia.org/wiki/Solar_System'},
            {'title': 'Internet', 'url': 'https://en.wikipedia.org/wiki/Internet'},
            {'title': 'Python (programming language)', 'url': 'https://en.wikipedia.org/wiki/Python_(programming_language)'}
        ]

def get_article_summary(url):
    """Get a summary of the Wikipedia article"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the first paragraph as summary
        paragraphs = soup.find_all('p')
        summary = "No summary available"
        for p in paragraphs:
            if p.text.strip() and len(p.text.strip()) > 50:  # Ensure it's substantial
                summary = p.text[:300] + '...' if len(p.text) > 300 else p.text
                break
                
        # Get the article image if available
        image_url = None
        
        # Try main infobox image first
        infobox = soup.find('table', {'class': 'infobox'})
        if infobox:
            img_tag = infobox.find('img')
            if img_tag and img_tag.get('src'):
                image_url = 'https:' + img_tag.get('src') if img_tag.get('src').startswith('//') else img_tag.get('src')
        
        # If no infobox image, try first image in content
        if not image_url:
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if content_div:
                img_tag = content_div.find('img')
                if img_tag and img_tag.get('src'):
                    image_url = 'https:' + img_tag.get('src') if img_tag.get('src').startswith('//') else img_tag.get('src')
        
        # Last resort - use a default Wikipedia image
        if not image_url:
            image_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/200px-Wikipedia-logo-v2.svg.png'
                
        return {
            'summary': summary,
            'image_url': image_url
        }
    except Exception as e:
        print(f"Error fetching article summary: {e}")
        return {
            'summary': 'Error fetching article',
            'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/200px-Wikipedia-logo-v2.svg.png'
        }

def get_articles_by_tag(tag):
    """Get Wikipedia articles by tag/category"""
    if tag in topic_articles_cache:
        return topic_articles_cache[tag]
    
    try:
        # Search Wikipedia for the tag
        search_url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={tag}&format=json&utf8='
        response = requests.get(search_url)
        data = response.json()
        
        articles = []
        if 'query' in data and 'search' in data['query']:
            for item in data['query']['search'][:15]:  # Limit to 15 articles
                title = item['title']
                url = f'https://en.wikipedia.org/wiki/{title.replace(" ", "_")}'
                
                articles.append({
                    'title': title,
                    'url': url
                })
        
        # Cache results
        topic_articles_cache[tag] = articles
        return articles
    except Exception as e:
        print(f"Error fetching articles for tag {tag}: {e}")
        return []

# Get available tags
def get_available_tags():
    return [
        "Technology", "Science", "Entertainment", "Sports", "Politics", 
        "Health", "History", "Art", "Music", "Literature"
    ]

@app.route('/')
def home():
    tags = get_available_tags()
    return render_template('index.html', tags=tags)

@app.route('/api/trending')
def api_trending():
    page = int(request.args.get('page', 1))
    topics = get_trending_topics()
    
    # Basic pagination to enable infinite scroll
    start_index = (page - 1) * 5
    end_index = start_index + 5
    
    # Get subset of topics for this page
    page_topics = topics[start_index:end_index] if start_index < len(topics) else []
    
    # Enhance with article summaries
    for topic in page_topics:
        summary_data = get_article_summary(topic['url'])
        topic.update(summary_data)
    
    return jsonify({
        'topics': page_topics,
        'has_more': end_index < len(topics)
    })

@app.route('/api/tags/<tag>')
def api_tag(tag):
    page = int(request.args.get('page', 1))
    articles = get_articles_by_tag(tag)
    
    # Basic pagination
    start_index = (page - 1) * 5
    end_index = start_index + 5
    
    # Get subset of articles for this page
    page_articles = articles[start_index:end_index] if start_index < len(articles) else []
    
    # Enhance with article summaries
    for article in page_articles:
        summary_data = get_article_summary(article['url'])
        article.update(summary_data)
    
    return jsonify({
        'articles': page_articles,
        'has_more': end_index < len(articles)
    })

if __name__ == '__main__':
    app.run(debug=True)