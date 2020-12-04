#! /usr/bin/env python3

"""
Methods for putting and getting a single message.
"""

import json
import os

import kafka


BOOTSTRAP_SERVERS=[
    'k0.kafka.local:9092',
    'k1.kafka.local:9092',
    'k2.kafka.local:9092'
]


def put_message(topic, message, producer=None):
    if not producer:
        producer = kafka.KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
    producer.send(topic, message)
    return producer

def get_next_message(topic, consumer=None, group_id=None, client_id=None):
    if not consumer:
        if not group_id:
            group_id = 'plain'
        if not client_id:
            client_id = "plain_%s" % (os.getpid())
        consumer = kafka.KafkaConsumer(topic, bootstrap_servers=BOOTSTRAP_SERVERS, group_id=group_id, client_id=client_id)
    print(">>> %s" % (json.dumps(consumer.metrics(), sort_keys=True, indent=4)))
    yield from consumer
