import asyncio
import logging
from typing import Any

import orjson

from ..base import JSONCooker
from .data import (
    AVATAR_SKILL_LEVEL,
    BUDDY_LEVEL_ADVANCE,
    BUDDY_STAR,
    CALLING_CARD_CONFIG,
    EQUIPMENT,
    EQUIPMENT_LEVEL,
    TITLE_CONFIG,
    WEAPON_LEVEL,
    WEAPON_STAR,
)

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

    def EnhanceRate(self) -> None:
        Items = self.deobfuscations["Items"]
        EnhanceRate = next(
            (k for k, v in self._data["weapon_level"][Items][1].items() if v == 1568),
            None,
        )
        if EnhanceRate is None:
            raise ValueError("Failed to find EnhanceRate in 'weapon_level'")
        self.deobfuscations["EnhanceRate"] = EnhanceRate

    def Exp(self) -> None:
        Items = self.deobfuscations["Items"]
        Exp = next(
            (k for k, v in self._data["weapon_level"][Items][1].items() if v == 60),
            None,
        )
        if Exp is None:
            raise ValueError("Failed to find Exp in 'weapon_level'")
        self.deobfuscations["Exp"] = Exp

    def ExpRecycleRate(self) -> None:
        Items = self.deobfuscations["Items"]
        ExpRecycleRate = next(
            (k for k, v in self._data["weapon_level"][Items][0].items() if v == 10000),
            None,
        )
        if ExpRecycleRate is None:
            raise ValueError("Failed to find ExpRecycleRate in 'weapon_level'")
        self.deobfuscations["ExpRecycleRate"] = ExpRecycleRate

    def Star(self) -> None:
        Items = self.deobfuscations["Items"]
        Star = next(
            (k for k, v in self._data["buddy_star"][Items][1].items() if v == 2),
            None,
        )
        if Star is None:
            raise ValueError("Failed to find Star in 'buddy_star'")
        self.deobfuscations["Star"] = Star

    def ItemID(self) -> None:
        Items = self.deobfuscations["Items"]
        ItemID = next(
            (
                k
                for i in self._data["equipment"][Items]
                for k, v in i.items()
                if v == 31021
            ),
            None,
        )
        if ItemID is None:
            raise ValueError("Failed to find ItemID in 'equipment'")
        self.deobfuscations["ItemID"] = ItemID

    def ID(self) -> None:
        Items = self.deobfuscations["Items"]
        ID = next(
            (
                k
                for k, v in self._data["avatar_skill_level"][Items][0].items()
                if v == 1011001
            ),
            None,
        )
        if ID is None:
            raise ValueError("Failed to find ID in 'avatar_skill_level'")
        self.deobfuscations["ID"] = ID

    def AvatarID(self) -> None:
        Items = self.deobfuscations["Items"]
        AvatarID = next(
            (
                k
                for k, v in self._data["avatar_skill_level"][Items][0].items()
                if v == 1011
            ),
            None,
        )
        if AvatarID is None:
            raise ValueError("Failed to find AvatarID in 'avatar_skill_level'")
        self.deobfuscations["AvatarID"] = AvatarID

    def SkillMaterials(self) -> None:
        Items = self.deobfuscations["Items"]
        ItemID = self.deobfuscations["ItemID"]

        for k, v in self._data["avatar_skill_level"][Items][0].items():
            print(k, v)

        SkillMaterials = next(
            (
                k
                for k, v in self._data["avatar_skill_level"][Items][0].items()
                if isinstance(v, list) and v and v[0][ItemID] == 10
            ),
            None,
        )
        if SkillMaterials is None:
            raise ValueError("Failed to find SkillMaterials in 'avatar_skill_level'")
        self.deobfuscations["SkillMaterials"] = SkillMaterials

    def BreakLevel(self) -> None:
        Items = self.deobfuscations["Items"]
        BreakLevel = next(
            (
                k
                for k, v in self._data["buddy_level_advance"][Items][2].items()
                if v == 2
            ),
            None,
        )
        if BreakLevel is None:
            raise ValueError("Failed to find BreakLevel in 'buddy_level_advance'")
        self.deobfuscations["BreakLevel"] = BreakLevel

    def StarRate(self) -> None:
        Items = self.deobfuscations["Items"]
        StarRate = next(
            (k for k, v in self._data["weapon_star"][Items][1].items() if v == 8922),
            None,
        )
        if StarRate is None:
            raise ValueError("Failed to find StarRate in 'weapon_star'")
        self.deobfuscations["StarRate"] = StarRate

    def RandRate(self) -> None:
        Items = self.deobfuscations["Items"]
        RandRate = next(
            (k for k, v in self._data["weapon_star"][Items][1].items() if v == 3000),
            None,
        )
        if RandRate is None:
            raise ValueError("Failed to find RandRate in 'weapon_star'")
        self.deobfuscations["RandRate"] = RandRate

    def TitleID(self) -> None:
        Items = self.deobfuscations["Items"]
        TitleID = next(
            (
                k
                for k, v in self._data["title_config"][Items][0].items()
                if v == 3800100
            ),
            None,
        )
        if TitleID is None:
            raise ValueError("Failed to find TitleID in 'title_config'")
        self.deobfuscations["TitleID"] = TitleID

    def TitleText(self) -> None:
        Items = self.deobfuscations["Items"]
        TitleText = next(
            (
                k
                for item in self._data["title_config"][Items]
                for k, v in item.items()
                if isinstance(v, str) and "TitleText" in v
            ),
            None,
        )
        if TitleText is None:
            raise ValueError("Failed to find TitleText in 'title_config'")
        self.deobfuscations["TitleText"] = TitleText

    def ColorA(self) -> None:
        Items = self.deobfuscations["Items"]
        ColorA = next(
            (
                k
                for k, v in self._data["title_config"][Items][0].items()
                if v == "e6e9ea"
            ),
            None,
        )
        if ColorA is None:
            raise ValueError("Failed to find ColorA in 'title_config'")
        self.deobfuscations["ColorA"] = ColorA

    def ColorB(self) -> None:
        Items = self.deobfuscations["Items"]
        ColorB = next(
            (
                k
                for k, v in self._data["title_config"][Items][0].items()
                if v == "8ea3ae"
            ),
            None,
        )
        if ColorB is None:
            raise ValueError("Failed to find ColorB in 'title_config'")
        self.deobfuscations["ColorB"] = ColorB

    def CallingCardID(self) -> None:
        Items = self.deobfuscations["Items"]
        CallingCardID = next(
            (
                k
                for item in self._data["namecards"][Items]
                for k, v in item.items()
                if v == 3300001
            ),
            None,
        )
        if CallingCardID is None:
            raise ValueError("Failed to find CallingCardID in 'namecards'")
        self.deobfuscations["CallingCardID"] = CallingCardID

    def Icon(self) -> None:
        Items = self.deobfuscations["Items"]
        icon_path = "Assets/NapResources/UI/Sprite/A1DynamicLoad/FriendCard/UnPacker/ImgCardCommon01.png"
        Icon = next(
            (
                k
                for item in self._data["namecards"][Items]
                for k, v in item.items()
                if v == icon_path
            ),
            None,
        )
        if Icon is None:
            raise ValueError("Failed to find Icon in 'namecards'")
        self.deobfuscations["Icon"] = Icon

    def deobfuscate(self) -> dict[str, Any]:
        self.Items()
        self.Rarity()
        self.Level()
        self.EnhanceRate()
        self.Exp()
        self.ExpRecycleRate()
        self.Star()
        self.ItemID()
        self.ID()
        self.AvatarID()
        self.SkillMaterials()
        self.BreakLevel()
        self.StarRate()
        self.RandRate()
        self.TitleID()
        self.TitleText()
        self.ColorA()
        self.ColorB()
        self.CallingCardID()
        self.Icon()

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
            self._download(EQUIPMENT, "equipment"),
            self._download(WEAPON_LEVEL, "weapon_level"),
            self._download(WEAPON_STAR, "weapon_star"),
            self._download(BUDDY_STAR, "buddy_star"),
            self._download(BUDDY_LEVEL_ADVANCE, "buddy_level_advance"),
            self._download(AVATAR_SKILL_LEVEL, "avatar_skill_level"),
            self._download(TITLE_CONFIG, "title_config"),
            self._download(CALLING_CARD_CONFIG, "namecards"),
        ]
        await asyncio.gather(*tasks)

    async def _cook_titles(self) -> None:
        title_config = self._data["title_config"]
        result: dict[str, Any] = {}

        for item in title_config["Items"]:
            result[str(item["TitleID"])] = {
                "TitleText": item["TitleText"],
                "ColorA": item["ColorA"],
                "ColorB": item["ColorB"],
            }

        await self._save_data("zzz/titles", result)

    async def _cook_namecards(self) -> None:
        namecards = self._data["namecards"]
        result: dict[str, Any] = {}

        for item in namecards["Items"]:
            result[str(item["CallingCardID"])] = {
                "Icon": f"/ui/zzz/{item['Icon'].split('/')[-1]}",
            }

        await self._save_data("zzz/namecards", result)

    async def cook(self) -> None:
        await self._download_files()

        deobfuscator = ZZZDeobfuscator(self._data)
        self._data = deobfuscator.deobfuscate()
        await self._save_data("zzz/deobfuscations", deobfuscator.deobfuscations)

        await self._save_data("zzz/equipment_level", self._data["equipment_level"])
        await self._save_data("zzz/weapon_level", self._data["weapon_level"])
        await self._save_data("zzz/weapon_star", self._data["weapon_star"])

        await self._cook_titles()
        await self._cook_namecards()

        LOGGER_.info("Done!")
