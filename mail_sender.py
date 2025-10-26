from mailjet_rest import Client
import os


class MailSender:

    def __init__(self, mailjet_client=None):
        api_key = os.environ['MJ_APIKEY_PUBLIC']
        api_secret = os.environ['MJ_APIKEY_PRIVATE']

        if not api_key or not api_secret:
            raise ValueError("MailJet environment variables are not set")

        self.mailjet_client = mailjet_client or Client(auth=(api_key, api_secret), version='v3.1')

    def send_mail(self, receiver, content, topic):
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "jez9.stas@gmail.com",
                        "Name": "Bluesky Summarizer Team"
                    },
                    "To": [
                        {
                            "Email": f"{receiver}",
                            "Name": "You"  # no "you" information
                        }
                    ],
                    "Subject": f"Summary about {topic}",
                    "TextPart": f"{content}",
                    "HTMLPart": f"{content}"
                }
            ]
        }
        result = self.mailjet_client.send.create(data=data)
        print("result of sending_mail: ", result.json())
