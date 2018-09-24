# -*- encoding: utf-8 -*-
import asyncio
import json
import random


class ClientProtocol(asyncio.Protocol):
    def __init__(self, a, b, loop):
        self.message = json.dumps({
            'a': a,
            'b': b,
        }).encode('ascii')
        self.loop = loop

    def connection_made(self, transport):
        transport.write(self.message)
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        answer = json.loads(data)['answer']
        print('Answer received: {!r}'.format(answer))

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()


loop = asyncio.get_event_loop()
coro = loop.create_connection(
    lambda: ClientProtocol(random.randint(-1000, 1000), random.randint(-1000, 1000), loop),
    '127.0.0.1', 8888
)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()
