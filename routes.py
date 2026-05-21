import secrets

from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
import os
import re

from post_summarizer import PostSummarizer
from database import Database
from dotenv import load_dotenv
from mail_sender import MailSender

load_dotenv()

app = Flask(__name__)
CORS(app)

_summarizer_instance = None
_db_instance = None
_mail_sender_instance = None


def get_mail_sender():
    global _mail_sender_instance
    if _mail_sender_instance is None:
        _mail_sender_instance = MailSender()
    return _mail_sender_instance


def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def get_summarizer():
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = PostSummarizer()
    return _summarizer_instance


TOPIC_MAX_LENGTH = 40
ALLOWED_TOPIC_PATTERN = re.compile(r'^[\w \-#+@.]+$')


def sanitize_topic(topic: str) -> str:
    if not topic or not isinstance(topic, str):
        raise ValueError("Topic must be a non-empty string.")
    topic = topic.strip()
    if len(topic) > TOPIC_MAX_LENGTH:
        raise ValueError(f"Topic must be {TOPIC_MAX_LENGTH} characters or fewer.")
    if not ALLOWED_TOPIC_PATTERN.match(topic):
        raise ValueError("Topic contains invalid characters.")
    return topic


def register_new_topic(email, topic):
    topic = sanitize_topic(topic)
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
def register_topic_endpoint():
    json = request.get_json()
    if not json.get("email") or not json.get("topic"):
        return jsonify(error="Bad request", message="missing either email, topic or both"), 400

    return register_new_topic(json.get("email"), json.get("topic"))


@app.route("/summary/<topic>")
def summarize_ai(topic):
    summary = get_summary(topic)
    response_body = {
        "topic": topic,
        "summary": summary
    }
    return make_response(jsonify(response_body), 200)


def get_summary(topic):
    summarizer = get_summarizer()
    posts = summarizer.get_latest_posts(topic)
    if len(posts) > 0:
        summary = summarizer.call_zen_ai(posts)
    else:
        summary = "No posts have been found on this subject of matter"
    return summary


@app.route("/trigger/summaries/send")
def send_summaries():
    key = request.headers.get('X-API-Key')
    if not secrets.compare_digest(os.environ.get('SENDING_KEY'), key):
        return make_response("invalid key", 400)
    for entry in get_db().get_users():
        summary = get_summary(entry[1])
        get_mail_sender().send_mail(entry[0], summary, entry[1])

    return make_response("", 200)
