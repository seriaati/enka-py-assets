import logging
from typing import Any

import aiofiles
import aiohttp
import orjson

LOGGER_ = logging.getLogger(__name__)


class JSONCooker:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._data: dict[str, Any] = {}

    async def _download(self, url: str, name: str) -> None:
        LOGGER_.info("Downloading %s from %s", name, url)
        async with self._session.get(url) as resp:
            self._data[name] = orjson.loads(await resp.text(encoding="utf-8"))

    async def _save_data(self, name: str, data: Any) -> None:
        LOGGER_.info("Saving %s.json...", name)
        async with aiofiles.open(f"data/{name}.json", "w", encoding="utf-8") as f:
            bytes_ = orjson.dumps(data)
            await f.write(bytes_.decode())
