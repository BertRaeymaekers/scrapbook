#! /usr/bin/env python3

"""
Get a message from topic one and put it on topic two after transformation.

Get a message from topic one, urlencode it and put it on topic two in an infinite loop.
"""


import put_get


if __name__ == "__main__":

    for msg in put_get.get_next_message('one'):
        print("---")
        print(msg.headers)
        print(msg.value)
