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


class KafkaConsumer():

    def __init__(self, topic, **kwargs):
        self.consumer = kafka.KafkaConsumer(topic, **kwargs)

    def __enter__(self):
        #print(">>> %s" % (json.dumps(self.consumer.metrics(), sort_keys=True, indent=4)))
        return self.consumer

    def __exit__(self, type, value, traceback):
        self.consumer.close(autocommit=True)


def put_message(topic, message, producer=None):
    if not producer:
        producer = kafka.KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
    producer.send(topic, message)
    return producer

def get_next_message(topic, group_id=None, client_id=None):
    if not group_id:
        group_id = 'plain_' + topic
    if not client_id:
        client_id = "plain_%s_%s" % (topic, os.getpid())
    with KafkaConsumer(topic, bootstrap_servers=BOOTSTRAP_SERVERS, group_id=group_id, client_id=client_id, enable_auto_commit=False) as consumer:
        for msg in consumer:
            yield (consumer, msg)
            # 'enable_auto_commit=True' seems the default best options (speed + commit), but very small chance of loosing a message?
            # Commit after every message, makes it much slower.
            #consumer.commit()
            # Alternative asynchronous commit is much better performance wise, but does it commit everything?
            #consumer.commit_async(callback=print)
