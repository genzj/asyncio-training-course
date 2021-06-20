# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
import select
import socket
from typing import Any, Coroutine, List, Tuple

IDLE = 'IDLE'

sock: socket.socket
recv_buf: List = []
send_buf: List = []


def create_datagram_endpoint(address: str):
    global sock
    try:
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        sock.bind((address, 0))
        sock.setblocking(True)
    except:
        if sock is not None:
            sock.close()
        raise
    print(f'socket {sock.getsockname()} created')


def poll_socket():
    global sock
    ready_to_read, ready_to_write, _ = select.select(
        [sock],
        [sock],
        [],
        0  # timeout=0 indicates no blocking
    )
    if ready_to_read:
        recv_buf.append(ready_to_read[0].recvfrom(1024))
    if send_buf and ready_to_write:
        buf, addr = send_buf.pop(0)
        ready_to_write[0].connect(addr)
        ready_to_write[0].send(buf)


def receive():
    while not recv_buf:
        yield IDLE
    return recv_buf.pop(0)


def send(bs: bytes, addr):
    send_buf.append((bs, addr))
    yield IDLE


def simulate_sleep(n):
    enter = datetime.utcnow()
    to = enter + timedelta(seconds=n)
    while datetime.utcnow() < to:
        yield IDLE


def background_task():
    while True:
        print('background task is alive')
        yield simulate_sleep(3)


def reverse_server():
    create_datagram_endpoint('127.0.0.1')
    while True:
        buf, addr = yield receive()
        print(f'got message from {addr}: {buf}')
        yield send(buf[::-1], addr)


class Stack:
    value: Any = None
    tasks: Tuple[Coroutine, ...] = tuple()

    def __init__(self, tasks: Tuple[Coroutine, ...]) -> None:
        self.value = None
        self.tasks = tasks

    @staticmethod
    def create_task(task: Coroutine) -> 'Stack':
        return Stack((task,))


def schedule(stack: Stack):
    tasks = stack.tasks
    value = stack.value

    if not tasks:
        return

    current, rest = tasks[0], tasks[1:]
    try:
        child = current.send(value)
        if value:
            value = None
    except StopIteration as ex:
        print('task %s returns %s' % (current, ex.value))
        value = ex.value
        tasks = rest
    else:
        if child is IDLE:
            poll_socket()
        else:
            tasks = (
                child,
                current,
            ) + rest
    stack.tasks = tasks
    stack.value = value


def gather(*tasks):
    stacks = tuple(Stack.create_task(task) for task in tasks)
    before = datetime.utcnow()
    print(before, 'scheduling begin')

    while stacks:
        top, rest = stacks[0], stacks[1:]
        schedule(top)
        if top.tasks:
            stacks = rest + (top,)
        else:
            stacks = rest

    done = datetime.utcnow()
    print(
        done,
        'scheduling done, %ss elapsed' % ((done - before).total_seconds(),)
    )


gather(
    background_task(),
    reverse_server(),
)
