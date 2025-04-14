import asyncio
import logging
from typing import Any

import orjson

from ..base import JSONCooker
from ..utils import async_error_handler
from .data import EQUIPMENT_LEVEL

LOGGER_ = logging.getLogger(__name__)


class ZZZDeobfuscator:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.deobfuscations: dict[str, str] = {}

    def Data(self) -> None:
        Data = next(iter(self._data["equipment_level"]), None)
        if Data is None:
            raise ValueError("Failed to find Data in 'equipment_level'")
        self.deobfuscations["Data"] = Data

    def Rarity(self) -> None:
        Data = self.deobfuscations["Data"]
        Rarity = next(
            (k for k, v in self._data["equipment_level"][Data][0].items() if v == 2),
            None,
        )
        if Rarity is None:
            raise ValueError("Failed to find Rarity in 'equipment_level'")
        self.deobfuscations["Rarity"] = Rarity

    def Level(self) -> None:
        Data = self.deobfuscations["Data"]
        Level = next(
            (k for k, v in self._data["equipment_level"][Data][1].items() if v == 1),
            None,
        )
        if Level is None:
            raise ValueError("Failed to find Level in 'equipment_level'")
        self.deobfuscations["Level"] = Level

    def deobfuscate(self) -> dict[str, Any]:
        self.Data()
        self.Rarity()
        self.Level()

        LOGGER_.info("Deobfuscations: %s", self.deobfuscations)

        for k, v in self._data.items():
            str_v = orjson.dumps(v).decode()
            for deobfuscated, obfuscated in self.deobfuscations.items():
                str_v = str_v.replace(obfuscated, deobfuscated)
            self._data[k] = orjson.loads(str_v)

        return self._data


class ZZZJSONCooker(JSONCooker):
    async def _download_files(self) -> None:
        tasks = [
            self._download(EQUIPMENT_LEVEL, "equipment_level"),
        ]
        await asyncio.gather(*tasks)

    async def cook(self) -> None:
        await self._download_files()

        deobfuscator = ZZZDeobfuscator(self._data)
        self._data = deobfuscator.deobfuscate()
        await self._save_data("zzz/deobfuscations", deobfuscator.deobfuscations)

        await self._save_data("zzz/equipment_level", self._data["equipment_level"])

        LOGGER_.info("Done!")
