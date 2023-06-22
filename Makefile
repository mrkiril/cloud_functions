PUBSUB_PROJECT_ID=my-project
TOPIC_ID=my-topic
PUSH_SUBSCRIPTION_ID=my-subscription
PUBSUB_EMULATOR_HOST=pubsub:8085

PIP_REQUIREMENTS_FILE = requirements/test.txt

include .env
export


build:
	docker-compose build --parallel --build-arg PIP_REQUIREMENTS_FILE="$(PIP_REQUIREMENTS_FILE)"

up: build
	docker-compose up
	docker-compose ps

down:
	docker-compose down --remove-orphans

create-topic:
	docker compose exec pubsub python3 python-pubsub/samples/snippets/publisher.py $PUBSUB_PROJECT_ID create $TOPIC_ID
	docker compose exec pubsub python3 python-pubsub/samples/snippets/subscriber.py $PUBSUB_PROJECT_ID create-push $TOPIC_ID $PUSH_SUBSCRIPTION_ID http://cfservice:8080

publish:
	docker compose exec pubsub python3 python-pubsub/samples/snippets/publisher.py $PUBSUB_PROJECT_ID publish $TOPIC_ID
