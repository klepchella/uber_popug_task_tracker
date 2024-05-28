import json

from kafka import KafkaConsumer

from task_tracker.database import session as db_session
from task_tracker.repository import UserRepository
from task_tracker.settings import settings_

consumer = KafkaConsumer(
    "account",
    bootstrap_servers=[settings_.kafka_host],
)


def get_session():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


account_repository = UserRepository(session=next(get_session()))

while True:
    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        print(
            "%s:%d:%d: key=%s value=%s"
            % (
                message.topic,
                message.partition,
                message.offset,
                message.key.decode(),
                message.value.decode(),
            )
        )
        account_repository.listen_user_info(
            key=message.key.decode(), value=json.loads(message.value.decode())
        )
