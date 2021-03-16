#! /usr/bin/env python3

"""
Get a message from topic one and put it on topic two after transformation.

Get a message from topic one, urlencode it and put it on topic two in an infinite loop.
"""


import base64
import datetime

import put_get


if __name__ == "__main__":

    start_time = 0

    for (consumer, msg) in put_get.get_next_message('one'):
        if not start_time:
            start_time = datetime.datetime.now().timestamp()
        id = int(msg.value[:10], 16)
        transformed_msg = base64.b64encode(msg.value)
        if id == 0:
            print("ONE %s: %s (%s)" % (id, transformed_msg, datetime.datetime.now().timestamp() - start_time))
        # We have 1000 messages waiting (partitions=1, consumers=1):
        #   get+transform:                      0.367 seconds (0.0004 sec/message)
        #   get+transform+put:                145.777 seconds (0.1457 sec/message)
        #   get+transform+put+commit_on_get:  156.590 seconds (0.1566 sec/message)
        # (partitions=2, consumers=2):
        #   get+transform+put+commit_on_get:   83.607 seconds (0.0836 sec/message)
        # (partitions=4, consumers=4):
        #   get+transform+put+commit_on_get:   43.761 seconds (0.0438 sec/message)
        # (partitions=4, consumers=1):
        #   get+transform+put+commit_on_get:  189.571 seconds (0.1896 sec/message)
        #                                     161.674 seconds (0.1617 sec/message)
        #                                     170.595 seconds (0.1706 sec/message)
        # (partitions=4, consumers=2):
        #   get+transform+put+commit_on_get:   68.024   78.629
        #                                      75.603  101.549
        #                                      80.782  108.902
        #                                      87.995   81.461
        #                                      45.384   60.290
        #                                      60.304  -15.023
        #                                     108.953   85.955
        put_get.put_message('two', transformed_msg)
        consumer.commit()

# kafka.errors.KafkaTimeoutError