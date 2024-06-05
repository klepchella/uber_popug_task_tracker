from kafka import KafkaProducer

from settings import settings_

producer = KafkaProducer(
    bootstrap_servers=[settings_.kafka_host],
)
