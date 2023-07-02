# -*- encoding: utf-8 -*-
import asyncio
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
    return hashlib.md5(to_sign.encode('utf-8')).hexdigest()


async def fetch(session, url, params):
    async with session.get(url, params=params) as response:
        return await response.json()


async def hefeng(session):
    url = 'https://devapi.qweather.com/v7/weather/now'
    params = {
        "location": "101020100",  # LocationID of Shanghai
        "publicid": "HE1601211533111623",
        "t": str(utctimestamp())
    }
    params['sign'] = sign(params, 'd5bd328dd36844bbb20c0e4905568e8e')

    return await fetch(session, url, params)


async def openweathermap(session):
    url = 'https://api.openweathermap.org/data/2.5/weather'

    params = {
        "q": "Shanghai",
        "appid": "18bc2f96c466fc82cd607d43eb152055",
        "units": "metric",
    }
    return await fetch(session, url, params)


async def main():
    async with aiohttp.ClientSession() as session:
        answer = {
            "hefeng": await hefeng(session),
            "openweathermap": await openweathermap(session)
        }
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
