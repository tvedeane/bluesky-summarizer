import libsql
import os


class Database:
    def __init__(self):
        url = os.getenv("TURSO_DATABASE_URL")
        auth_token = os.getenv("TURSO_AUTH_TOKEN")

        self.conn = libsql.connect("summarizer", sync_url=url, auth_token=auth_token)
        self.conn.sync()

    def user(self, email: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO users (email) VALUES (?);",
            (email,)
        )
        self.conn.commit()
        user = self.conn.execute(
            "SELECT * FROM users WHERE email = ?;",
            (email,)
        ).fetchone()
        return user

    def topic_already_followed(self, email, topic):
        topics_count = self.conn.execute(
            "SELECT COUNT(*) FROM users JOIN registered_topics ON users.id = registered_topics.user_id "
            "WHERE email = ? AND topic = ?",
            (email, topic,)
        ).fetchone()

        return topics_count[0] != 0

    def save_topic(self, email, topic):
        try:
            user = self.user(email)
            if user is not None:
                self.conn.execute(
                    "INSERT INTO  registered_topics (user_id, topic) VALUES (?, ?)",
                    (user[0], topic,)
                )
                self.conn.commit()
                return True
            return False
        except ValueError as e:
            print("Error saving topic: ", e)
            return False
