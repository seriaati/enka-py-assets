import asyncio
import logging
from typing import Any

import orjson

from ..base import JSONCooker
from .data import EQUIPMENT_LEVEL, WEAPON_LEVEL, WEAPON_STAR

LOGGER_ = logging.getLogger(__name__)


class ZZZDeobfuscator:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.deobfuscations: dict[str, str] = {}

    def Items(self) -> None:
        Items = next(iter(self._data["equipment_level"]), None)
        if Items is None:
            raise ValueError("Failed to find Items in 'equipment_level'")
        self.deobfuscations["Items"] = Items

    def Rarity(self) -> None:
        Items = self.deobfuscations["Items"]
        Rarity = next(
            (k for k, v in self._data["equipment_level"][Items][0].items() if v == 2),
            None,
        )
        if Rarity is None:
            raise ValueError("Failed to find Rarity in 'equipment_level'")
        self.deobfuscations["Rarity"] = Rarity

    def Level(self) -> None:
        Items = self.deobfuscations["Items"]
        Level = next(
            (k for k, v in self._data["equipment_level"][Items][1].items() if v == 1),
            None,
        )
        if Level is None:
            raise ValueError("Failed to find Level in 'equipment_level'")
        self.deobfuscations["Level"] = Level

    def deobfuscate(self) -> dict[str, Any]:
        self.Items()
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
            self._download(WEAPON_LEVEL, "weapon_level"),
            self._download(WEAPON_STAR, "weapon_star"),
        ]
        await asyncio.gather(*tasks)

    async def cook(self) -> None:
        await self._download_files()

        deobfuscator = ZZZDeobfuscator(self._data)
        self._data = deobfuscator.deobfuscate()
        await self._save_data("zzz/deobfuscations", deobfuscator.deobfuscations)

        await self._save_data("zzz/equipment_level", self._data["equipment_level"])
        await self._save_data("zzz/weapon_level", self._data["weapon_level"])
        await self._save_data("zzz/weapon_star", self._data["weapon_star"])

        LOGGER_.info("Done!")
