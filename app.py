from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

WIKI_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"

def extract_links(html_text):
    """Extract potential links for next topics from Wikipedia content"""
    soup = BeautifulSoup(html_text, "html.parser")
    links = []
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if href.startswith("/wiki/") and ":" not in href:
            link_text = a.text.strip()
            if link_text and link_text not in links:
                links.append(link_text)
    return links[:5]  # Return only a few links for better UX

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_article", methods=["GET"])
def get_article():
    topic = request.args.get("topic", "Python_(programming_language)")
    response = requests.get(WIKI_API_URL + topic)

    if response.status_code == 200:
        data = response.json()
        return jsonify({
            "title": data.get("title", "Unknown Title"),
            "extract": data.get("extract", "No summary available."),
            "links": extract_links(data.get("extract_html", ""))
        })
    return jsonify({"error": "Article not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
