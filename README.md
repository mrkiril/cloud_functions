Cloud Functions Pub/Sub Tutorial
===============================
This tutorial shows how to configure a Python application to receive messages from a
[Pub/Sub](https://cloud.google.com/pubsub/docs/overview) topic.

This sample is based on the
[Cloud Functions quickstart](https://cloud.google.com/functions/docs/quickstart-pubsub)
page with using the UnixSocket for communication between the Cloud Function and the Postgres

> In .env file you can find variables for connection to the Postgres and Pub/Sub

## Setup
```bash
make up
```

After it push some messages to the Pub/Sub topic
```bash
make publish
```
