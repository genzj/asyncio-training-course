# -*- encoding: utf-8 -*-
import asyncio
import json


class AddServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = json.loads(data)
        print('Data received from {!r}: {!r}'.format(addr, message))

        answer = {
            'answer': message.get('a', 0) + message.get('b', 0)
        }
        print('Send: {!r}'.format(answer))
        self.transport.sendto(json.dumps(answer).encode('ascii'), addr)


loop = asyncio.get_event_loop()
print("Starting UDP server")
# One protocol instance will be created to serve all client requests
listen = loop.create_datagram_endpoint(
    AddServerProtocol, local_addr=('127.0.0.1', 9999))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
