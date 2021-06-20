# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta

IDLE = 'IDLE'


def simulate_sleep(n):
    enter = datetime.utcnow()
    to = enter + timedelta(seconds=n)
    while datetime.utcnow() < to:
        yield IDLE
    return n


def create():
    ret = yield simulate_sleep(3.0)
    print(datetime.utcnow(), "(1) create file", f"{ret=}")


def write():
    ret = yield simulate_sleep(1.0)
    print(datetime.utcnow(), "(2) write into file", f"{ret=}")


def close():
    print(datetime.utcnow(), "(3) close file")
    yield IDLE


def schedule(task):
    polling_io = 0
    all_tasks = (task,)
    value = None
    before = datetime.utcnow()
    print(before, 'scheduling begin')
    while all_tasks:
        current, rest = all_tasks[0], all_tasks[1:]
        try:
            child = current.send(value)
            if value:
                value = None
        except StopIteration as ex:
            print('task %s returns %s' % (current, ex.value))
            value = ex.value
            all_tasks = rest
        else:
            if child is IDLE:
                # idle is a special state reserved for IO polling
                polling_io += 1
            else:
                all_tasks = (child, current,) + rest
    done = datetime.utcnow()
    print(
        done,
        'scheduling done, %ss elapsed' % ((done - before).total_seconds(),)
    )
    print(f'IO polling happened {polling_io} times')


def chain():
    yield create()
    yield write()
    yield close()
    print(datetime.utcnow(), 'tasks completed')


schedule(chain())
