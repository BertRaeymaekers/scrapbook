#! /usr/bin/env python3


import asyncio
from asyncapi import build_api


async def publish(channel_id, message) -> None:
    await api.connect()
    await api.publish(channel_id, message)
    await api.disconnect()


if __name__ == "__main__":
    api = build_api('kafka.yml')
    channel_id = "one"
    message = api.payload(channel_id, id=00001, message='ABC')
