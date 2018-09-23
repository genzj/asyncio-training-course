# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta


def simulate_sleep(n):
    enter = datetime.utcnow()
    to = enter + timedelta(seconds=n)
    while datetime.utcnow() < to:
        yield


def create():
    for _ in simulate_sleep(3.0):
        yield
    print(datetime.utcnow(), "(1) create file")


def write():
    for _ in simulate_sleep(1.0):
        yield
    print(datetime.utcnow(), "(2) write into file")


def close():
    print(datetime.utcnow(), "(3) close file")
    yield


def scheduler(*tasks):
    before = datetime.utcnow()
    print(before, 'scheduling begin')
    while tasks:
        current, rest = tasks[0], tasks[1:]
        try:
            next(current)
        except StopIteration:
            print('task %s ends' % (current,))
            tasks = rest
        else:
            tasks = rest + (current,)
    done = datetime.utcnow()
    print(done, 'scheduling done, %ss elapsed' % ((done - before).total_seconds(),))


def chain():
    for _ in create():
        yield _
    for _ in write():
        yield _
    for _ in close():
        yield _
    print(datetime.utcnow(), 'all task done')


def fan_out():
    return [create(), write(), close()]


scheduler(chain())
scheduler(*fan_out())
