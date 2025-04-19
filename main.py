import os
from google import genai
from atproto import Client
from atproto_client.models.app.bsky.feed.search_posts import Params


class PostSummarizer:
    Elon_Musk = "Elon Musk"  # input("Topic: ")

    def __init__(self, genai_client=None, bsky_client=None):
        genai_key = os.environ.get('GENAIKEY')
        if not genai_key and not genai_client:
            raise ValueError("GENAIKEY environment variable is not set")
        self.genai_client = genai_client or genai.Client(api_key=genai_key)
        bsky_key = os.environ.get('BSKYPASS')
        if not bsky_key and not bsky_client:
            raise ValueError("BSKYPASS environment variable is not set")
        self.bsky_client = bsky_client or Client()
        self.bsky_client.login('5tasiu.bsky.social', bsky_key)

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

    def generate_response(self, latest_posts):
        ai_prompt = "summarize these posts: "  # input("Action: ")
        reply = self.genai_client.models.generate_content(
            model="gemini-2.0-flash", contents=f"{ai_prompt} {latest_posts}"
        )
        print(reply.text)
        with open("responses.txt", "a") as f:
            print(reply.text, file=f)


if __name__ == '__main__':
    summarizer = PostSummarizer()
    posts = summarizer.get_latest_posts("UCL")
    if len(posts) >= 0:
        summarizer.generate_response(posts)
