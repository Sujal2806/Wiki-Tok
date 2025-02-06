from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

WIKI_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_article")
def get_article():
    topic = request.args.get("topic")
    if not topic:
        return jsonify({"error": "No topic provided"}), 400

    response = requests.get(WIKI_API_URL + topic)
    if response.status_code != 200:
        return jsonify({"error": "Article not found"}), 404

    data = response.json()
    return jsonify({
        "title": data.get("title", "No Title"),
        "extract": data.get("extract", "No summary available."),
        "page_url": f"https://en.wikipedia.org/wiki/{topic}"
    })

if __name__ == "__main__":
    app.run(debug=True)
