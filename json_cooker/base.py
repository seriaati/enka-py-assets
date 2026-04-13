import asyncio
import logging
from pathlib import Path
from typing import Any

import aiofiles
import aiohttp
import orjson

LOGGER_ = logging.getLogger(__name__)


class JSONCooker:
    def __init__(self, session: aiohttp.ClientSession | None) -> None:
        self._session = session
        self._data: dict[str, Any] = {}

    _game: str

    @property
    def _raw_dir(self) -> Path:
        return Path(f"raw_data/{self._game}")

    async def _download(self, url: str, name: str) -> None:
        if self._session is None:
            raise RuntimeError("Cannot download: session is None")
        LOGGER_.info("Downloading %s from %s", name, url)
        try:
            async with self._session.get(url) as resp:
                self._data[name] = orjson.loads(await resp.text(encoding="utf-8"))
        except Exception as e:
            LOGGER_.error("Failed to download %s: %s", name, e)
            raise e

    async def _save_raw(self, name: str) -> None:
        self._raw_dir.mkdir(parents=True, exist_ok=True)
        path = self._raw_dir / f"{name}.json"
        LOGGER_.info("Saving raw %s...", name)
        try:
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(orjson.dumps(self._data[name]).decode())
        except Exception as e:
            LOGGER_.error("Failed to save raw %s: %s", name, e)
            raise e

    async def _load_raw(self, name: str) -> None:
        path = self._raw_dir / f"{name}.json"
        LOGGER_.info("Loading raw %s...", name)
        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as f:
                self._data[name] = orjson.loads(await f.read())
        except Exception as e:
            LOGGER_.error("Failed to load raw %s: %s", name, e)
            raise e

    async def _load_all_raw(self) -> None:
        paths = list(self._raw_dir.glob("*.json"))
        await asyncio.gather(*[self._load_raw(p.stem) for p in paths])

    async def _save_data(self, name: str, data: Any) -> None:
        LOGGER_.info("Saving %s.json...", name)
        try:
            async with aiofiles.open(f"data/{name}.json", "w", encoding="utf-8") as f:
                bytes_ = orjson.dumps(
                    data, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
                )
                await f.write(bytes_.decode())
        except Exception as e:
            LOGGER_.error("Failed to save %s: %s", name, e)
            raise e
