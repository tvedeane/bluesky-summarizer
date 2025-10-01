import unittest
from unittest.mock import MagicMock
import json

from google.genai.errors import ServerError

from bluesky_summarizer import app
from routes import set_db, set_summarizer
from post_summarizer import PostSummarizer


class TestPostSummarizer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @staticmethod
    def setup_mocks():
        genai_mock = MagicMock()
        genai_mock.models.generate_content.return_value.text = "Summary of posts"
        bsky_mock = MagicMock()
        mock_search_posts = MagicMock()
        bsky_mock.app.bsky.feed.search_posts.return_value = mock_search_posts

        mock_post1 = MagicMock()
        mock_post1.record.text = "This is a test post about Elon Musk"
        mock_post1.author.display_name = "Test User 1"

        mock_post2 = MagicMock()
        mock_post2.record.text = "Another test post about Elon Musk"
        mock_post2.author.display_name = "Test User 2"

        mock_search_posts.posts = [mock_post1, mock_post2]

        return genai_mock, bsky_mock

    @staticmethod
    def setup_db_mock():
        db_mock = MagicMock()
        db_mock.user.return_value = (1, "test@example.com")  # Mock user with id=1
        db_mock.topic_already_followed.return_value = False
        db_mock.save_topic.return_value = True
        return db_mock

    def test_get_posts_with_mocks(self):
        genai_mock, bsky_mock = self.setup_mocks()

        summarizer_test = PostSummarizer(genai_mock, bsky_mock)
        posts = summarizer_test.get_latest_posts("UCL")
        summary = summarizer_test.call_ai(posts)

        genai_mock.models.generate_content.assert_called_with(
            model='gemini-2.0-flash',
            contents="summarize these posts:  ['[New Post] Test User 1: This is a test post about Elon Musk', "
                     "'[New Post] Test User 2: Another test post about Elon Musk']")
        self.assertEqual(summary, "Summary of posts")

    def test_env_variables(self):
        genai_mock = MagicMock()
        bsky_mock = MagicMock()

        with self.assertRaises(ValueError) as context:
            PostSummarizer(None, bsky_mock)
        self.assertEqual(str(context.exception), "GENAIKEY environment variable is not set")

        with self.assertRaises(ValueError) as context:
            PostSummarizer(genai_mock, None)
        self.assertEqual(str(context.exception), "BSKYLOGIN environment variable is not set")

    def test_ai_not_called_without_posts(self):
        genai_mock = MagicMock()
        bsky_mock = MagicMock()
        mock_search_posts = MagicMock()
        mock_search_posts.posts = []
        summarizer_test = PostSummarizer(genai_mock, bsky_mock)
        posts = summarizer_test.get_latest_posts("UCL")
        summarizer_test.call_ai(posts)

        genai_mock.models.generate_response.assert_not_called()

    def test_ai_call_retried_when_error(self):
        genai_mock, bsky_mock = self.setup_mocks()

        genai_mock.models.generate_content.side_effect = [
            ServerError(code=502, response_json=MagicMock(), response=""),
            MagicMock(text="Summary of posts")
        ]

        summarizer_test = PostSummarizer(genai_mock, bsky_mock)
        posts = summarizer_test.get_latest_posts("UCL")
        summary = summarizer_test.call_ai(posts)

        self.assertEqual(genai_mock.models.generate_content.call_count, 2)
        self.assertEqual(summary, "Summary of posts")

    def test_json_response(self):
        genai_mock, bsky_mock = self.setup_mocks()

        set_summarizer(PostSummarizer(genai_mock, bsky_mock))
        response = self.app.get('/summary/Elon%20Musk')
        data = json.loads(response.data)
        self.assertEqual("Summary of posts", data["summary"])
        self.assertEqual("Elon Musk", data["topic"])

    def test_register_new_topic_wrong_input(self):
        genai_mock, bsky_mock = self.setup_mocks()
        db_mock = self.setup_db_mock()

        set_summarizer(PostSummarizer(genai_mock, bsky_mock))
        set_db(db_mock)
        response = self.app.post('/topic/register', json={"name": "Flask"})
        self.assertEqual(400, response.status_code)
        db_mock.topic_already_followed.assert_not_called()
        db_mock.save_topic.assert_not_called()

    def test_register_new_topic(self):
        genai_mock, bsky_mock = self.setup_mocks()
        db_mock = self.setup_db_mock()

        set_summarizer(PostSummarizer(genai_mock, bsky_mock))
        set_db(db_mock)
        response = self.app.post('/topic/register', json={
            "email": "flask@python.io",
            "topic": "Guido",
        })
        self.assertEqual(201, response.status_code)
        self.assertIn('Guido', response.get_data(as_text=True))
        db_mock.topic_already_followed.assert_called_with('flask@python.io', 'Guido')
        db_mock.save_topic.assert_called_with('flask@python.io', 'Guido')
