# -*- encoding: utf-8 -*-
import asyncio
import base64
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
    md5 = hashlib.md5(to_sign.encode('utf-8')).digest()
    return base64.b64encode(md5).decode('ascii')


async def fetch(session, url, params):
    async with session.get(url, params=params) as response:
        return await response.json()


async def hefeng(session, city):
    url = 'https://free-api.heweather.com/s6/weather/now'
    params = {
        "location": city,
        "username": "HE1601211533111623",
        "t": str(utctimestamp())
    }
    params['sign'] = sign(params, 'd5bd328dd36844bbb20c0e4905568e8e')

    return {
        'source': 'hefeng',
        'result': await fetch(session, url, params)
    }


async def openweathermap(session, city):
    url = 'https://api.openweathermap.org/data/2.5/weather'

    params = {
        "q": city,
        "appid": "18bc2f96c466fc82cd607d43eb152055",
        "units": "metric",
    }
    return {
        'source': 'openweathermap',
        'result': await fetch(session, url, params)
    }


async def main(loop):
    answer = dict()
    async with aiohttp.ClientSession() as session:
        done, pending = await asyncio.wait([
            hefeng(session, 'Shanghai'),
            openweathermap(session, 'Shanghai'),
        ])
        writes = []
        for task in done:
            data = task.result()
            source = data['source']
            result = data['result']
            answer[source] = result
            writes.append(loop.run_in_executor(None, write_file, source, result))
            # write_file(source, result)
        await asyncio.wait(writes)
    return answer


def write_file(source, result):
    with open('%s.json' % (source,), 'w', encoding='utf-8') as out:
        json.dump(result, out, ensure_ascii=False, indent=2, sort_keys=True)
    time.sleep(1)


def run():
    loop = asyncio.get_event_loop()
    before = datetime.now()
    answer = loop.run_until_complete(main(loop))
    done = datetime.now()
    pprint(answer)
    print('%ss elapsed' % ((done - before).total_seconds()))


if __name__ == '__main__':
    run()
