# -*- encoding: utf-8 -*-
import asyncio
import json


async def handle_add(reader, writer):
    data = await reader.read(100)
    message = json.loads(data)

    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))

    answer = {
        'answer': message.get('a', 0) + message.get('b', 0)
    }

    print("Send: %r" % answer)
    writer.write(json.dumps(answer).encode('ascii'))
    await writer.drain()

    print("Close the client socket")
    writer.close()


loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_add, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)

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
