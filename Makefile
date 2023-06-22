PIP_REQUIREMENTS_FILE=requirements/test.txt

include .env
export

create-topic:
	docker compose exec pubsub python3 publisher.py $(PUBSUB_PROJECT_ID) create $(TOPIC_ID)
	docker compose exec pubsub python3 subscriber.py $(PUBSUB_PROJECT_ID) create-push $(TOPIC_ID) $(PUSH_SUBSCRIPTION_ID) $(CF_SERVER_HOST)

publish:
	docker compose exec pubsub python3 publisher.py $(PUBSUB_PROJECT_ID) publish $(TOPIC_ID)

build:
	docker-compose build --parallel --build-arg PIP_REQUIREMENTS_FILE="$(PIP_REQUIREMENTS_FILE)"

up: build
	docker-compose up
	docker-compose ps
	make create-topic

down:
	docker-compose down --remove-orphans


