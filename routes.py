from flask import Flask, jsonify, make_response, request, g
from flask_cors import CORS

from post_summarizer import PostSummarizer
from database import Database
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


def get_db():
    if 'db' not in g:
        g.db = Database()
    return g.db


def get_summarizer():
    if 'summarizer' not in g:
        g.summarizer = PostSummarizer()
    return g.summarizer


def register_new_topic(email, topic):
    if get_db().topic_already_followed(email, topic):
        return jsonify(message="You cannot follow the same topic twice"), 400
    if get_db().save_topic(email, topic):
        response_body = {
            "topic": topic,
            "summary": "Topic successfully registered"
        }
        return jsonify(message=response_body), 201
    return jsonify(error="Server Error", message="Server Error"), 500


@app.route("/topic/register", methods=["POST"])
# Invoke-RestMethod -Uri "http://127.0.0.1:5000/topic/register" `
# -Method POST `
# -Body '{"email": "test2", "topic": "test"}' `
# -ContentType "application/json"
def register_topic_endpoint():
    json = request.get_json()
    if not json.get("email") or not json.get("topic"):
        return jsonify(error="Bad request", message="missing either email, topic or both"), 400

    return register_new_topic(json.get("email"), json.get("topic"))


@app.route("/summary/<topic>")
def summarize_ai(topic):
    summarizer = get_summarizer()
    posts = summarizer.get_latest_posts(topic)
    print(len(posts))
    if len(posts) > 0:
        summary = summarizer.call_ai(posts)
    else:
        summary = "No posts have been found on this subject of matter"
    print(summary)

    response_body = {
        "topic": topic,
        "summary": summary
    }
    return make_response(jsonify(response_body), 200)
