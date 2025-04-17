import os
from google import genai
from atproto import Client
from atproto_client.models.app.bsky.feed.search_posts import Params


Elon_Musk = "Elon Musk"  # input("Topic: ")
ai_prompt = "summarize these posts: "  # input("Action: ")
genaiClient = genai.Client(api_key=os.environ['GENAIKEY'])


def get_latest_posts(topic=Elon_Musk):
    latest_day_posts = []
    client = Client()
    client.login('5tasiu.bsky.social', os.environ['BSKYPASS'])

    params = Params(q=f"{topic}", sort="top")
    search_posts = client.app.bsky.feed.search_posts(params)

    for feed_item in search_posts.posts:
        action = 'New Post'

        post = feed_item.record
        author = feed_item.author

        latest_day_posts.append(f'[{action}] {author.display_name}: {post.text}')
    return latest_day_posts


def generate_response(latest_posts):

    reply = genaiClient.models.generate_content(
        model="gemini-2.0-flash", contents=f"{ai_prompt} {latest_posts}"
    )
    print(reply.text)
    with open("responses.txt", "a") as f:
        print(reply.text, file=f)


if __name__ == '__main__':
    posts = get_latest_posts("UCL")
    generate_response(posts)
