import asyncio
import logging

import aiohttp

from json_cooker.genshin.cooker import GenshinJSONCooker
from json_cooker.hsr.cooker import HSRJSONCooker


async def main() -> None:
    handler = logging.StreamHandler()
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    fmt = logging.Formatter(
        "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(fmt)
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    async with aiohttp.ClientSession() as session:
        cooker = GenshinJSONCooker(session)
        await cooker.cook()

        cooker = HSRJSONCooker(session)
        await cooker.cook()


asyncio.run(main())
