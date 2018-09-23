# -*- encoding: utf-8 -*-
import asyncio
import base64
import hashlib
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

    return await fetch(session, url, params)


async def openweathermap(session, city):
    url = 'https://api.openweathermap.org/data/2.5/weather'

    params = {
        "q": city,
        "appid": "18bc2f96c466fc82cd607d43eb152055",
        "units": "metric",
    }
    return await fetch(session, url, params)


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = {
            "hefeng": hefeng(session, 'Shanghai'),
            "openweathermap": openweathermap(session, 'Shanghai')
        }
        answer = {}
        names = []
        coroutines = []
        for k, v in tasks.items():
            names.append(k)
            coroutines.append(v)
        for name, result in zip(names, await asyncio.gather(*coroutines)):
            answer[name] = result
    return answer


def run():
    loop = asyncio.get_event_loop()
    before = datetime.now()
    answer = loop.run_until_complete(main())
    done = datetime.now()
    pprint(answer)
    print('%ss elapsed' % ((done - before).total_seconds()))


if __name__ == '__main__':
    run()
