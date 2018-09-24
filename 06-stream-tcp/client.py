# -*- encoding: utf-8 -*-
import asyncio
import json
import random


async def client(a, b, loop):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888,
        loop=loop
    )

    message = json.dumps({
        'a': a,
        'b': b,
    })

    print('Send: %r' % message)
    writer.write(message.encode('ascii'))

    data = await reader.read(100)
    answer = json.loads(data)
    print('Answer received: %s' % answer['answer'])

    print('Close the socket')
    writer.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(client(random.randint(-1000, 1000), random.randint(-1000, 1000), loop))
loop.close()
