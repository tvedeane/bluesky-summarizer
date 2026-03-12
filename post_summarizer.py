from retry import retry
import os
from atproto import Client
from google import genai
from openai import OpenAI
from atproto_client.models.app.bsky.feed.search_posts import Params


class PostSummarizer:
    Elon_Musk = "Elon Musk"

    def __init__(self, genai_client=None, bsky_client=None, openai_client=None):
        zenai_key = os.environ.get('ZENAIKEY')
        if not zenai_key and not openai_client:
            raise ValueError("ZENAIKEY environment variable is not set")
        self.openai_client = openai_client or OpenAI(
            api_key=zenai_key,
            base_url="https://opencode.ai/zen/v1",
        )

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
    def call_google_ai(self, latest_posts):
        print("calling ai...")
        ai_prompt = "summarize these posts: "
        reply = self.genai_client.models.generate_content(
            model="gemini-2.0-flash", contents=f"{ai_prompt} {latest_posts}"
        )
        return reply.text

    @retry(tries=3, delay=3, backoff=2)
    def call_zen_ai(self, latest_posts):

        ai_prompt = "summarize these posts: "  # input("Action: ")
        response = self.openai_client.chat.completions.create(
            model="big-pickle",
            messages=[
                {"role": "user", "content": f"{ai_prompt} {latest_posts}"}
            ],
        )

        return response.choices[0].message.content
