# -*- encoding: utf-8 -*-
import asyncio
import json


class AddServerProtocol(asyncio.Protocol):

    async def add(self, a, b):
        await asyncio.sleep(1)
        return a + b

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = json.loads(data)
        print('Data received: {!r}'.format(message))

        task = asyncio.create_task(
            self.add(message.get('a', 0), message.get('b', 0))
        )

        task.add_done_callback(self.add_done)

    def add_done(self, task):
        answer = {'answer': task.result()}
        print('Send: {!r}'.format(answer))
        self.transport.write(json.dumps(answer).encode('ascii'))

        print('Close the client socket')
        self.transport.close()


loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(AddServerProtocol, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)
assert server.sockets

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
