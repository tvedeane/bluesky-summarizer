from flask import Flask, jsonify, make_response, request
from flask_cors import CORS

from post_summarizer import PostSummarizer
from database import Database
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

global_db = None


def get_db():
    global global_db
    if global_db is None:
        global_db = Database()
    return global_db


db = get_db()


# For testing purposes - allows injection of mock database
def set_db(custom_db):
    global global_db
    global_db = custom_db


global_summarizer = None


def get_summarizer():
    global global_summarizer
    if global_summarizer is None:
        global_summarizer = PostSummarizer()
    return global_summarizer


# For testing purposes - allows injection of mock summarizer
def set_summarizer(custom_summarizer):
    global global_summarizer
    global_summarizer = custom_summarizer


def register_new_topic(email, topic):
    if db.topic_already_followed(email, topic):
        return jsonify(message="You cannot follow the same topic twice"), 400
    if db.save_topic(email, topic):
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
