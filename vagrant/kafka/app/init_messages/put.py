#! /usr/bin/env python3

"""
Putting 1000 messages on topic 'one'
"""


import secrets

import kafka


if __name__ == "__main__":
    producer = kafka.KafkaProducer(bootstrap_servers='k0.kafka.local:9092')
    for i in range(1000):
        producer.send('one', secrets.token_bytes(100))
    producer.flush()
