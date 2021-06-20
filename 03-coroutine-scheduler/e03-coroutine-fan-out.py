# -*- encoding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Any, Coroutine, Tuple

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
            pass
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


def chain():
    yield create()
    yield write()
    yield close()
    print(datetime.utcnow(), 'tasks completed')


# gather(chain())
gather(
    create(),
    write(),
    close(),
)
