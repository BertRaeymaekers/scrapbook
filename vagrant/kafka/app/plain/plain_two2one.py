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

    for (consumer, msg) in put_get.get_next_message('two'):
        if not start_time:
            start_time = datetime.datetime.now().timestamp()
        transformed_msg = base64.b64decode(msg.value)
        id = int(transformed_msg[:10], 16)
        if id == 0:
            print("TWO %s: %s (%s)" % (id, transformed_msg, datetime.datetime.now().timestamp() - start_time))
        put_get.put_message('one', transformed_msg)
        consumer.commit()
