# -*- encoding: utf-8 -*-
import time
from collections import namedtuple
from datetime import datetime, timedelta


def simulate_sleep(n):
    enter = datetime.utcnow()
    to = enter + timedelta(seconds=n)
    while datetime.utcnow() < to:
        time.sleep(n / 2.0)
        yield


def async_add(a, b):
    # simulate async IO operation
    yield simulate_sleep(0.1)
    # Note: use StopIteration in Python 2.x
    # raise StopIteration(a + b)
    return a + b


def async_sum(*args):
    s, args = args[0], args[1:]
    for num in args:
        s = yield async_add(s, num)
    # Note: use StopIteration in Python 2.x
    # raise StopIteration(s)
    return s


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


l1 = list(range(10))
l2 = list(range(5))
answers = loop(async_sum(*l1), async_sum(*l2))
print('answers: %s %s' % (answers[0], answers[1]))
