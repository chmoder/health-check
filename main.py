from __future__ import annotations

import asyncio
import time
from typing import List, Dict
from urllib.parse import urlparse

import yaml
from aiohttp import ClientSession

from classes import Request

INPUT_FILE = './input.yaml'


def parse_config() -> []:
    fp = open(INPUT_FILE, 'r')
    raw_config = yaml.safe_load(fp)
    fp.close()

    config = [Request(**x) for x in raw_config]
    return config


async def fetch(session: ClientSession, url: str, method: str, headers: dict | None, body: str | None) -> dict:
    start = time.time() * 1000
    async with session.request(method, url, headers=headers, data=body, timeout=15) as response:
        delta_ms = (time.time() * 1000 - start)

        valid_status = 200 <= response.status <= 299
        valid_latency = 0 <= delta_ms < 500
        is_up = valid_status and valid_latency

        host = urlparse(url).hostname

        return {'host': host, 'is_up': is_up}


def calculate_uptime(all_checks: List[Dict]) -> dict:
    """
    converts from: [{'host': 'example.com', 'is_up': True}]
    to: {'example.com': {'up': 0, 'total': 0, 'uptime': 0}}
    :param all_checks:
    :return:
    """
    processed_checks = { item["host"]: {'up': 0, 'total': 0, 'uptime': 0} for item in all_checks }

    for check in all_checks:
        host_name = check.get('host')
        is_up = check.get('is_up')

        if is_up:
            processed_checks[host_name]['up'] += 1

        processed_checks[host_name]['total'] += 1
        processed_checks[host_name]['uptime'] = int((processed_checks[host_name]['up'] / processed_checks[host_name]['total']) * 100)

    return processed_checks


async def main():
    config = parse_config()
    all_checks = []

    while True:
        async with ClientSession() as session:
            tasks = []
            for request in config:
                f = fetch(
                    session,
                    request.url,
                    request.method,
                    headers=request.headers,
                    body=request.body
                )
                tasks.append(f)

            responses = await asyncio.gather(*tasks)

        all_checks.extend(responses)
        processed_checks = calculate_uptime(all_checks)

        for host, values in processed_checks.items():
            print(f'{host} has {values["uptime"]}% availability percentage')

        time.sleep(15)


if __name__ == "__main__":
    asyncio.run(main())
