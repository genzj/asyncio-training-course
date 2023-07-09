# -*- encoding: utf-8 -*-
import asyncio
import hashlib
import json
import time
from datetime import datetime
from pprint import pprint

import aiohttp


def utctimestamp():
    unix_time_source = datetime(1970, 1, 1)
    n = datetime.utcnow()
    return int((n - unix_time_source).total_seconds())


def sign(params, secret):
    to_sign = ''
    # 先将参数以其参数名的字典序升序进行排序
    params = sorted(params.items(), key=lambda item: item[0])
    # 遍历排序后的参数数组中的每一个key/value对
    for k, v in params:
        if k != 'sign' and k != 'key' and v != '':
            to_sign += k + '=' + v + '&'
    to_sign = to_sign[:-1]
    to_sign += secret
    return hashlib.md5(to_sign.encode('utf-8')).hexdigest()


async def fetch(session, url, params):
    async with session.get(url, params=params) as response:
        return await response.json()


async def hefeng(loop, session):
    url = 'https://devapi.qweather.com/v7/weather/now'
    params = {
        "location": "101020100",  # LocationID of Shanghai
        "publicid": "HE1601211533111623",
        "t": str(utctimestamp())
    }
    params['sign'] = sign(params, 'd5bd328dd36844bbb20c0e4905568e8e')

    data = await fetch(session, url, params)
    # write_file_sync("hefeng", data)
    await write_file_async(loop, "hefeng", data)
    return data


async def openweathermap(loop, session):
    url = 'https://api.openweathermap.org/data/2.5/weather'

    params = {
        "q": "Shanghai",
        "appid": "18bc2f96c466fc82cd607d43eb152055",
        "units": "metric",
    }
    data = await fetch(session, url, params)
    # write_file_sync("openweathermap", data)
    await write_file_async(loop, "openweathermap", data)
    return data


async def main(loop):
    async with aiohttp.ClientSession() as session:
        tasks = {
            "hefeng": hefeng(loop, session),
            "openweathermap": openweathermap(loop, session),
        }
        answer = {}
        names = list(tasks.keys())
        coroutines = list(tasks.values())
        for name, result in zip(names, await asyncio.gather(*coroutines)):
            answer[name] = result
    return answer


async def write_file_async(loop, source, result):
    await loop.run_in_executor(None, write_file_sync, source, result)


def write_file_sync(source, result):
    with open('%s.json' % (source,), 'w', encoding='utf-8') as out:
        json.dump(result, out, ensure_ascii=False, indent=2, sort_keys=True)
    time.sleep(3)


def run():
    loop = asyncio.get_event_loop()
    before = datetime.now()
    answer = loop.run_until_complete(main(loop))
    done = datetime.now()
    pprint(answer)
    print('%ss elapsed' % ((done - before).total_seconds()))


if __name__ == '__main__':
    run()
