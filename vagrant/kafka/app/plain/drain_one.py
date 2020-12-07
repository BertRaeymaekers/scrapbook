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
        print("DRAIN %s: %s (%s)" % (id, transformed_msg, datetime.datetime.now().timestamp() - start_time))
        consumer.commit()
