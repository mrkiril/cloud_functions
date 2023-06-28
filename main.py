import base64
import json
import os
import time

import functions_framework
from typing import Dict, TypedDict, Any
import logging.config
import sqlalchemy as sa

import requests
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from cloudevents.http.event import CloudEvent


logger = logging.getLogger(__name__)

SERVICE_ENVIRONMENT = os.getenv("SERVICE_ENVIRONMENT", "dev")
iS_DEV = SERVICE_ENVIRONMENT == "dev"
LOG_HANDLERS = ["default"] if iS_DEV else ["default"]

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(process)d] %(levelname)s-%(name)s::%(module)s:%(lineno)s:: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {"level": "INFO", "handlers": LOG_HANDLERS},
    },
}

logging.config.dictConfig(LOG_CONFIG)


def create_db_engine(
    database: str,
    user: str,
    password: str,
    connection_name: str,
    port: int | None = None,
    is_unix_socker: bool = True,
) -> sa.engine.base.Engine:
    """
    :param connection_name: You cant get it from GCP console
    """
    if is_unix_socker:
        if iS_DEV:
            unix_socket_path = connection_name
        else:
            unix_socket_path = f"/cloudsql/{connection_name}"
        url = sa.engine.url.URL.create(
            drivername="postgresql+psycopg2",
            username=user,
            password=password,
            host=unix_socket_path,
            database=database,
        )
    else:
        url = sa.engine.url.URL.create(
            drivername="postgresql+psycopg2",
            username=user,
            password=password,
            host=connection_name,
            port=port,
            database=database,
        )
    logger.info(f"Connection string: {url}")
    return sa.create_engine(
        url=url,
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800,
        pool_use_lifo=True,
        pool_pre_ping=True,
    )


db_engine = create_db_engine(
    database=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
    connection_name=os.environ['POSTGRES_CONNECTION_NAME'],
    port=int(os.environ['POSTGRES_PORT']),
    is_unix_socker=bool(int(os.environ['UNIX_SOCKET'])),
)


class PubSubMessage(TypedDict):
    data: str  # base64 encoded
    attributes: Dict[str, str]
    message_id: str
    publishTime: str


class WebhookMessage(TypedDict):
    user_webhook_request_id: str
    attributes: Dict[str, str]
    messageId: str
    publishTime: str


def get_event_data(event: CloudEvent) -> dict[str, Any]:
    return json.loads(base64.b64decode(event.data["message"].get("data")))


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello(cloud_event: CloudEvent):
    start_time = time.time()
    print("Entered the function")
    try:
        json_data = get_event_data(cloud_event)
    except json.decoder.JSONDecodeError as e:
        print(f"Error: {e}")
        json_data = dict(
            user_webhook_request_id="",
            attributes={},
            messageId="",
            publishTime="",
        )

    r = requests.get('https://postman-echo.com/get?foo1=bar1&foo2=bar2')
    logger.info("Status: %s", r.status_code)
    print("Content-type:", r.headers['content-type'])
    print(f"Body: {r.text[:15]}")

    db_time = time.time()
    db_session = sessionmaker(db_engine)
    with db_session.begin() as session:
        res = session.execute(text("SELECT 1;"))
        print(f"DB result: {res.first()}")
    print("= " * 30)
    print("= = = = = = = = = = END of the function = = = = = = = = = = ")
    print(f"= = = = = = = = = = DB time: {round(time.time() - db_time, 2)}")
    print(f"= = = = = = = = = = All time: {round(time.time() - start_time, 2)}")
    print("= " * 30)
