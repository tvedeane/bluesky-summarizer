import os

import unittest
from unittest.mock import MagicMock, patch
import json

from google.genai.errors import ServerError

from bluesky_summarizer import app
from post_summarizer import PostSummarizer


class TestPostSummarizer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @staticmethod
    def setup_mocks():
        zenai_mock = MagicMock()
        zenai_mock.chat.completions.create.choices[0].message.content = "Summary of posts"
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

        return genai_mock, bsky_mock, zenai_mock

    @staticmethod
    def setup_db_mock():
        db_mock = MagicMock()
        db_mock.user.return_value = (1, "test@example.com")  # Mock user with id=1
        db_mock.topic_already_followed.return_value = False
        db_mock.save_topic.return_value = True
        return db_mock

    def test_get_posts_with_mocks(self):
        genai_mock, bsky_mock, zenai_mock = self.setup_mocks()

        summarizer_test = PostSummarizer(genai_mock, bsky_mock)
        posts = summarizer_test.get_latest_posts("UCL")
        summary = summarizer_test.call_google_ai(posts)

        genai_mock.models.generate_content.assert_called_with(
            model='gemini-2.0-flash',
            contents="summarize these posts:  ['[New Post] Test User 1: This is a test post about Elon Musk', "
                     "'[New Post] Test User 2: Another test post about Elon Musk']")
        self.assertEqual(summary, "Summary of posts")

    def test_env_variables(self):
        genai_mock = MagicMock()
        bsky_mock = MagicMock()
        zenai_mock = MagicMock()

        with self.assertRaises(ValueError) as context:
            PostSummarizer(genai_mock, bsky_mock, None)
        self.assertEqual(str(context.exception), "ZENAIKEY environment variable is not set")

        with self.assertRaises(ValueError) as context:
            PostSummarizer(None, bsky_mock, zenai_mock)
        self.assertEqual(str(context.exception), "GENAIKEY environment variable is not set")

        with self.assertRaises(ValueError) as context:
            PostSummarizer(genai_mock, None, zenai_mock)
        self.assertEqual(str(context.exception), "BSKYLOGIN environment variable is not set")

    def test_ai_not_called_without_posts(self):
        genai_mock = MagicMock()
        bsky_mock = MagicMock()
        mock_search_posts = MagicMock()
        mock_search_posts.posts = []
        summarizer_test = PostSummarizer(genai_mock, bsky_mock)
        posts = summarizer_test.get_latest_posts("UCL")
        summarizer_test.call_google_ai(posts)

        genai_mock.models.generate_response.assert_not_called()

    def test_ai_call_retried_when_error(self):
        genai_mock, bsky_mock, zenai_mock = self.setup_mocks()

        genai_mock.models.generate_content.side_effect = [
            ServerError(code=502, response_json=MagicMock(), response=""),
            MagicMock(text="Summary of posts")
        ]

        summarizer_test = PostSummarizer(genai_mock, bsky_mock)
        posts = summarizer_test.get_latest_posts("UCL")
        summary = summarizer_test.call_google_ai(posts)

        self.assertEqual(genai_mock.models.generate_content.call_count, 2)
        self.assertEqual(summary, "Summary of posts")

    @patch('routes.get_summarizer')
    def test_json_response(self, mock_get_summarizer):
        genai_mock, bsky_mock, zenai_mock = self.setup_mocks()
        mock_get_summarizer.return_value = PostSummarizer(genai_mock, bsky_mock, zenai_mock)

        response = self.app.get('/summary/Elon%20Musk')
        data = json.loads(response.data)
        self.assertEqual("Summary of posts", data["summary"])
        self.assertEqual("Elon Musk", data["topic"])

    @patch('routes.get_summarizer')
    @patch('routes.get_db')
    def test_register_new_topic_wrong_input(self, mock_get_db, mock_get_summarizer):
        genai_mock, bsky_mock, zenai_mock = self.setup_mocks()
        db_mock = self.setup_db_mock()
        mock_get_db.return_value = db_mock
        mock_get_summarizer.return_value = PostSummarizer(genai_mock, bsky_mock)

        response = self.app.post('/topic/register', json={"name": "Flask"})
        self.assertEqual(400, response.status_code)
        db_mock.topic_already_followed.assert_not_called()
        db_mock.save_topic.assert_not_called()

    @patch('routes.get_summarizer')
    @patch('routes.get_db')
    def test_register_new_topic(self, mock_get_db, mock_get_summarizer):
        genai_mock, bsky_mock, zenai_mock = self.setup_mocks()
        db_mock = self.setup_db_mock()
        mock_get_db.return_value = db_mock
        mock_get_summarizer.return_value = PostSummarizer(genai_mock, bsky_mock)

        response = self.app.post('/topic/register', json={
            "email": "flask@python.io",
            "topic": "Guido",
        })
        self.assertEqual(201, response.status_code)
        self.assertIn('Guido', response.get_data(as_text=True))
        db_mock.topic_already_followed.assert_called_with('flask@python.io', 'Guido')
        db_mock.save_topic.assert_called_with('flask@python.io', 'Guido')

    @patch('routes.get_mail_sender')
    @patch('routes.get_summarizer')
    @patch('routes.get_db')
    def test_send_summaries(self, mock_get_db, mock_get_summarizer, mock_get_mail_sender):
        mail_sender_mock = MagicMock()
        mock_get_mail_sender.return_value = mail_sender_mock
        summarizer_mock = MagicMock()
        mock_get_summarizer.return_value = summarizer_mock
        db_mock = self.setup_db_mock()
        db_mock.get_users.return_value = [
            ("john@gmail.com", "Elon"),
            ("Joe@gmail.com", "Donald")
        ]

        mock_get_db.return_value = db_mock
        with patch.dict(os.environ, {'SENDING_KEY': '123'}):
            response = self.app.get('/trigger/summaries/send', headers={'X-API-Key': '123'})
            self.assertEqual(200, response.status_code)
            summarizer_mock.get_latest_posts.assert_any_call("Elon")
            summarizer_mock.get_latest_posts.assert_any_call("Donald")
            #assert call ai
            mail_sender_mock.send_mail.assert_any_call(
                "john@gmail.com", "No posts have been found on this subject of matter", "Elon")
            mail_sender_mock.send_mail.assert_any_call(
                "Joe@gmail.com", "No posts have been found on this subject of matter", "Donald")

