#! /usr/bin/env python3

"""
Put a number of random messages in a Kafka topic

Put in topic topic 'one'(*) 1000(*) random messages of size 100(*) with id starting at 0(*).
The first 10 bytes of the message is the id in hex.

(*) Can be overwritten with command line parameters:
    [topic [messagecount [messagesize [startid]]]]
"""

import secrets
import sys

import kafka


TOPIC = 'one'
LENGTH = 100
COUNT = 1000
START = 0


def put_messages(topic, count, length, start):
    # Sending random messages preceding with
    producer = kafka.KafkaProducer(bootstrap_servers='k0.kafka.local:9092')
    for i in range(count):
        producer.send(topic, hex(i + start)[2:].rjust(10,"0").encode() + secrets.token_bytes(LENGTH-10))
    producer.flush()


if __name__ == "__main__":

    # Topic, number of message, size of message, start number
    topic = TOPIC
    count = COUNT
    length = LENGTH
    start = START
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    if len(sys.argv) > 2:
        count = int(sys.argv[2])
    if len(sys.argv) > 3:
        length = int(sys.argv[3])
    if len(sys.argv) > 4:
        start = int(sys.argv[4])

    put_messages(topic, count, length, start)
