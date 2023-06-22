from google.cloud import pubsub_v1
import google.api_core.exceptions
import logging


PUBSUB_PROJECT_ID = "my-project"
TOPIC_ID = "my-topic1"
PUSH_SUBSCRIPTION_ID = "my-subscription"

# TODO(developer): Choose an existing topic.
# project_id = "your-project-id"
# topic_id = "your-topic-id"

publisher_options = pubsub_v1.types.PublisherOptions(enable_message_ordering=True)
# Sending messages to the same region ensures they are received in order
# even when multiple publishers are used.
client_options = {"api_endpoint": "localhost:8085"}
publisher = pubsub_v1.PublisherClient(
    publisher_options=publisher_options, client_options=client_options
)
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(PUBSUB_PROJECT_ID, TOPIC_ID)

for message in [
    ("message1", "key1"),
    # ("message2", "key2"),
    ("message3", "key1"),
    # ("message4", "key2"),
]:
    # Data must be a bytestring
    data = message[0].encode("utf-8")
    ordering_key = message[1]
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data=data, ordering_key=ordering_key)
    print(f"Published {data} on {topic_path} with ordering key {ordering_key}.")
    try:
        print(future.result())
    except RuntimeError:
        # Resume publish on an ordering key that has had unrecoverable errors.
        publisher.resume_publish(topic_path, ordering_key)
    except google.api_core.exceptions.NotFound as e:
        logging.info("Topic or subscription not found: %s", topic_path)
        publisher.resume_publish(topic_path, ordering_key)

print(f"Resumed publishing messages with ordering keys to {topic_path}.")
