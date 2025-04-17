import os

from google import genai
from atproto import Client
from atproto_client.models.app.bsky.feed.search_posts import Params
import sys

topic = "Elon Musk"  # input("Topic: ")
aiprompt = "summarize these posts: "  # input("Action: ")
latestDayPosts = []
genaiClient = genai.Client(api_key=os.environ['GENAIKEY'])


def main() -> None:

    client = Client()
    client.login('5tasiu.bsky.social', os.environ['BSKYPASS'])

    #  print('Home (Following):\n')

    # Get "Home" page. Use pagination (cursor + limit) to fetch all posts
    timeline = client.get_timeline(algorithm='reverse-chronological')

    params = Params(q=f"{topic}", sort="top")
    searchPosts = client.app.bsky.feed.search_posts(params)

    for feed_item in searchPosts.posts:
        action = 'New Post'
        # if feed_item.reason:
        #     action_by = feed_item.reason.by.handle
        #     action = f'Reposted by @{action_by}'

        post = feed_item.record
        author = feed_item.author

        #  print(f'[{action}] {author.display_name}: {post.text}')
        latestDayPosts.append(f'[{action}] {author.display_name}: {post.text}')


def generate_response():
    reply = genaiClient.models.generate_content(
        model="gemini-2.0-flash", contents=f"{aiprompt} {latestDayPosts}"
    )
    print(reply.text)
    with open("responses.txt", "a") as f:
        print(reply.text, file=f)


if __name__ == '__main__':
    main()
    generate_response()
