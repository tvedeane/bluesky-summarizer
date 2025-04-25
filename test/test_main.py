import unittest
from unittest.mock import patch, MagicMock
import json

from main import app, PostSummarizer, set_summarizer


class TestPostSummarizer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_posts_with_mocks(self):
        genai_mock = MagicMock()
        genai_mock.models.generate_content.return_value.text = "Summary of posts"
        bsky_mock = MagicMock()
        mock_search_posts = MagicMock()
        bsky_mock.app.bsky.feed.search_posts.return_value = mock_search_posts

        # Create mock post data
        mock_post1 = MagicMock()
        mock_post1.record.text = "This is a test post about Elon Musk"
        mock_post1.author.display_name = "Test User 1"

        mock_post2 = MagicMock()
        mock_post2.record.text = "Another test post about Elon Musk"
        mock_post2.author.display_name = "Test User 2"

        mock_search_posts.posts = [mock_post1, mock_post2]

        summarizer_test = PostSummarizer(genai_mock, bsky_mock)
        posts = summarizer_test.get_latest_posts("UCL")
        summary = summarizer_test.generate_response(posts)

        genai_mock.models.generate_content.assert_called_with(
            model='gemini-2.0-flash',
            contents="summarize these posts:  ['[New Post] Test User 1: This is a test post about Elon Musk', '[New Post] Test User 2: Another test post about Elon Musk']")
        self.assertEqual(summary, "Summary of posts")

    def test_clients(self):
        genai_mock = MagicMock()
        bsky_mock = MagicMock()

        with self.assertRaises(ValueError) as context:
            PostSummarizer(None, bsky_mock)
        self.assertEqual(str(context.exception), "GENAIKEY environment variable is not set")

        with self.assertRaises(ValueError) as context:
            PostSummarizer(genai_mock, None)
        self.assertEqual(str(context.exception), "BSKYPASS environment variable is not set")

    def test_response(self):
        genai_mock = MagicMock()
        bsky_mock = MagicMock()
        mock_search_posts = MagicMock()
        mock_search_posts.posts = []
        summarizer_test = PostSummarizer(genai_mock, bsky_mock)
        posts = summarizer_test.get_latest_posts("UCL")
        summarizer_test.generate_response(posts)

        genai_mock.models.generate_response.assert_not_called()

    def test_json_response(self):
        genai_mock = MagicMock()
        genai_mock.models.generate_content.return_value.text = "Summary of posts"
        bsky_mock = MagicMock()
        mock_search_posts = MagicMock()
        bsky_mock.app.bsky.feed.search_posts.return_value = mock_search_posts

        # Create mock post data
        mock_post1 = MagicMock()
        mock_post1.record.text = "This is a test post about Elon Musk"
        mock_post1.author.display_name = "Test User 1"

        mock_post2 = MagicMock()
        mock_post2.record.text = "Another test post about Elon Musk"
        mock_post2.author.display_name = "Test User 2"

        mock_search_posts.posts = [mock_post1, mock_post2]

        set_summarizer(PostSummarizer(genai_mock, bsky_mock))
        response = self.app.get('/summary/Elon%20Musk')
        data = json.loads(response.data)
        self.assertEqual("Summary of posts", data["summary"])
        self.assertEqual("Elon Musk", data["topic"])
