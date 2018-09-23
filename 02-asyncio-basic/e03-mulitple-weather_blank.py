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
    __?__


async def hefeng(session, city):
    url = 'https://free-api.heweather.com/s6/weather/now'
    params = {
        "location": city,
        "username": "HE1601211533111623",
        "t": str(utctimestamp())
    }
    params['sign'] = sign(params, 'd5bd328dd36844bbb20c0e4905568e8e')

    __?__


async def openweathermap(session, city):
    url = 'https://api.openweathermap.org/data/2.5/weather'

    params = {
        "q": city,
        "appid": "18bc2f96c466fc82cd607d43eb152055",
        "units": "metric",
    }
    __?__


async def main():
    async with aiohttp.ClientSession() as session:
        answer = __?__
    return answer


def run():
    __?__


if __name__ == '__main__':
    run()
