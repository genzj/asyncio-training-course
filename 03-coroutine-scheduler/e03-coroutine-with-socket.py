# -*- encoding: utf-8 -*-
import socket
from collections import namedtuple
from datetime import datetime, timedelta

from dns import rdatatype
from dns.message import make_query, from_wire


w_polling = 0
r_polling = 0


def simulate_sleep(n):
    enter = datetime.utcnow()
    to = enter + timedelta(seconds=n)
    while datetime.utcnow() < to:
        yield


def create_datagram_endpoint():
    sock = None
    try:
        sock = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM
        )
        sock.setblocking(False)
    except:
        if sock is not None:
            sock.close()
        raise
    return sock


def sock_send_to(sock, remote_addr, remote_port, data):
    global w_polling
    while True:
        try:
            n = sock.sendto(data, (remote_addr, remote_port))
            w_polling += 1
        except (BlockingIOError, InterruptedError):
            yield
        else:
            break
    return n


def sock_recv(sock: socket.socket, n):
    global r_polling
    while True:
        try:
            data, remote = sock.recvfrom(n)
            r_polling += 1
        except (BlockingIOError, InterruptedError):
            yield
        else:
            break
    return data, remote


def async_resolve(name, server, port=53):
    sock = create_datagram_endpoint()
    request = make_query(name, rdatatype.A)
    yield sock_send_to(sock, server, port, request.to_wire())
    response, remote = yield sock_recv(sock, 512)
    print('got %r from %s' % (response, remote))
    yield simulate_sleep(1)
    return from_wire(response), remote


Stack = namedtuple('Stack', 'value,tasks')


def schedule(stack: Stack):
    value, tasks = stack
    if tasks:
        current, rest = tasks[0], tasks[1:]
        try:
            child = current.send(value)
            value = None
        except StopIteration as ex:
            value = ex.value
            # print('task %s returns %s and ends' % (current, value))
            tasks = rest
        else:
            if child is not None:
                tasks = (child,) + tasks
    return Stack(value, tasks)


def loop(*coros):
    stacks = tuple(Stack(None, (task,)) for task in coros)
    values = tuple()
    while stacks:
        current, rest = stacks[0], stacks[1:]
        current = schedule(current)

        if current.tasks:
            stacks = rest + (current,)
        else:
            values = values + (current.value,)
            stacks = rest
    return values


domain_name = 'www.baidu.com'
servers = ['114.114.114.114', '114.114.115.115', '114.114.114.119', '114.114.115.119']
reqs = [async_resolve(domain_name, s) for s in servers]
before = datetime.utcnow()
answers = loop(*reqs)
done = datetime.utcnow()

for data, (remote_addr, remote_port) in answers:
    print('Server %s:%s reply:' % (remote_addr, remote_port))
    print(data.to_text())
    print('-' * 65)

print('%ss elapsed' % ((done - before).total_seconds(),))
print('send polling %d times, recv polling %d times' % (w_polling, r_polling))
