from google import genai
from atproto import Client
from atproto_client.models.app.bsky.feed.search_posts import Params
import sys

latestDayPosts = []
genaiClient = genai.Client(api_key="")
def main() -> None:

    client = Client()
    client.login('5tasiu.bsky.social', '')

    #print('Home (Following):\n')

    # Get "Home" page. Use pagination (cursor + limit) to fetch all posts
    timeline = client.get_timeline(algorithm='reverse-chronological')

    params = Params(q="Elon Musk", sort="top")
    searchPosts = client.app.bsky.feed.search_posts(params)

    for feed_item in searchPosts.posts:
        action = 'New Post'
        # if feed_item.reason:
        #     action_by = feed_item.reason.by.handle
        #     action = f'Reposted by @{action_by}'

        post = feed_item.record
        author = feed_item.author

        #print(f'[{action}] {author.display_name}: {post.text}')
        latestDayPosts.append(f'[{action}] {author.display_name}: {post.text}')


    for feed_item in timeline.feed:
        action = 'New Post'
        if feed_item.reason:
            action_by = feed_item.reason.by.handle
            action = f'Reposted by @{action_by}'

        post = feed_item.post.record
        author = feed_item.post.author

        #print(f'[{action}] {author.display_name}: {post.text}')

def Response():
    response = genaiClient.models.generate_content(
        model="gemini-2.0-flash", contents=f"summarize these posts {latestDayPosts}"
    )
    print(response.text)
    with open("responses.txt", "w") as f:
        print(response.text, file=f)

if __name__ == '__main__':
    main()
    Response()
