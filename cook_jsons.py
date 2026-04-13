import asyncio
import logging
import argparse
import sys

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
arg_parser.add_argument(
    "--no-dump",
    action="store_true",
    help="Only download raw data, skip cooking/dumping.",
    default=False,
)
arg_parser.add_argument(
    "--no-download",
    action="store_true",
    help="Skip downloading, load from raw cache and only run dump.",
    default=False,
)
args = arg_parser.parse_args()


async def main() -> None:
    if args.no_dump and args.no_download:
        print("Error: --no-dump and --no-download cannot both be set (nothing to do).")
        sys.exit(1)

    handler = logging.StreamHandler()
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    fmt = logging.Formatter(
        "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(fmt)
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    session: aiohttp.ClientSession | None = None

    async def run(cooker_cls: type) -> None:
        cooker = cooker_cls(session)
        if args.no_download:
            await cooker.dump()
        elif args.no_dump:
            await cooker.download()
        else:
            await cooker.cook()

    if args.no_download:
        if args.gi:
            await run(GenshinJSONCooker)
        if args.hsr:
            await run(HSRJSONCooker)
        if args.zzz:
            await run(ZZZJSONCooker)
    else:
        async with aiohttp.ClientSession() as s:
            session = s
            if args.gi:
                await run(GenshinJSONCooker)
            if args.hsr:
                await run(HSRJSONCooker)
            if args.zzz:
                await run(ZZZJSONCooker)


asyncio.run(main())
