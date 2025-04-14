import asyncio
import logging
import argparse

import aiohttp

from json_cooker.genshin.cooker import GenshinJSONCooker
from json_cooker.hsr.cooker import HSRJSONCooker
from json_cooker.zzz.cooker import ZZZJSONCooker

arg_parser = argparse.ArgumentParser(
    description="Cook JSON files for Genshin, HSR, and ZZZ."
)
arg_parser.add_argument(
    "--gi",
    action="store_true",
    help="Cook Genshin JSON files.",
    default=False,
)
arg_parser.add_argument(
    "--hsr",
    action="store_true",
    help="Cook HSR JSON files.",
    default=False,
)
arg_parser.add_argument(
    "--zzz",
    action="store_true",
    help="Cook ZZZ JSON files.",
    default=False,
)
args = arg_parser.parse_args()


async def main() -> None:
    handler = logging.StreamHandler()
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    fmt = logging.Formatter(
        "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(fmt)
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    async with aiohttp.ClientSession() as session:
        if args.gi:
            cooker = GenshinJSONCooker(session)
            await cooker.cook()

        if args.hsr:
            cooker = HSRJSONCooker(session)
            await cooker.cook()

        if args.zzz:
            cooker = ZZZJSONCooker(session)
            await cooker.cook()


asyncio.run(main())
