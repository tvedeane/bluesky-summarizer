import os
from google import genai
from atproto import Client
from atproto_client.models.app.bsky.feed.search_posts import Params
from flask import Flask, jsonify, make_response
from flask_cors import CORS
from retry import retry
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class PostSummarizer:
    Elon_Musk = "Elon Musk"  # input("Topic: ")

    def __init__(self, genai_client=None, bsky_client=None):
        genai_key = os.environ.get('GENAIKEY')
        if not genai_key and not genai_client:
            raise ValueError("GENAIKEY environment variable is not set")
        self.genai_client = genai_client or genai.Client(api_key=genai_key)

        bsky_login = os.environ.get('BSKYLOGIN')
        if not bsky_login and not bsky_client:
            raise ValueError("BSKYLOGIN environment variable is not set")
        bsky_key = os.environ.get('BSKYPASS')
        if not bsky_key and not bsky_client:
            raise ValueError("BSKYPASS environment variable is not set")
        self.bsky_client = bsky_client or Client()
        self.bsky_client.login(bsky_login, bsky_key)

    def get_latest_posts(self, topic=Elon_Musk):
        latest_day_posts = []
        params = Params(q=f"{topic}", sort="top")
        search_posts = self.bsky_client.app.bsky.feed.search_posts(params)

        for feed_item in search_posts.posts:
            action = 'New Post'
            post = feed_item.record
            author = feed_item.author

            latest_day_posts.append(f'[{action}] {author.display_name}: {post.text}')
        return latest_day_posts

    @retry(tries=3, delay=3, backoff=2)  # retry after 3 and 6 seconds
    def call_ai(self, latest_posts):
        print("calling ai...")
        ai_prompt = "summarize these posts: "  # input("Action: ")
        reply = self.genai_client.models.generate_content(
            model="gemini-2.0-flash", contents=f"{ai_prompt} {latest_posts}"
        )
        return reply.text


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


app = Flask(__name__)
CORS(app)


@app.route("/summary/<topic>")
def summarize_ai(topic):
    summarizer = get_summarizer()
    posts = summarizer.get_latest_posts(topic)
    summary = ""
    if len(posts) >= 0:
        summary = summarizer.call_ai(posts)
        print(summary)

    response_body = {
        "topic": topic,
        "summary": summary
    }
    return make_response(jsonify(response_body), 200)
