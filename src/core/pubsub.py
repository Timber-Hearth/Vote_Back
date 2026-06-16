import json
from typing import Any

from google.cloud import pubsub_v1


class PubSub():
    def __init__(self):
        self.PROJECT_ID = "secret-vote-back"
        self.TOPIC_ID = "make_qr"

        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(self.PROJECT_ID, self.TOPIC_ID)
        
    def MessageFromBytes(self, message: dict):
        data = json.dumps(message).encode("utf-8")
        return data
        
    def PublishManage(self, event_type: str,  message: dict[str, Any]) -> bool:
        try:
            pub_sub_data = {
                "event" : event_type,
                "data" : message
            }
            data = self.MessageFromBytes(pub_sub_data)
            future = self.publisher.publish(self.topic_path, data)
            future.result()
            return True
        except Exception as e:
            print(f"Error publishing message: {e}")
            return False