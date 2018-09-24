# -*- encoding: utf-8 -*-
import asyncio
import json
import random


class ClientProtocol:
    def __init__(self, a, b, loop):
        self.message = json.dumps({
            'a': a,
            'b': b,
        }).encode('ascii')
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print('Send:', self.message)
        self.transport.sendto(self.message)

    def datagram_received(self, data, addr):
        answer = json.loads(data)['answer']

        print('Answer received: {!r}'.format(answer))

        print("Close the socket")
        self.transport.close()

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()


loop = asyncio.get_event_loop()
connect = loop.create_datagram_endpoint(
    lambda: ClientProtocol(random.randint(-1000, 1000), random.randint(-1000, 1000), loop),
    remote_addr=('127.0.0.1', 9999)
)
transport, protocol = loop.run_until_complete(connect)
loop.run_forever()
transport.close()
loop.close()
