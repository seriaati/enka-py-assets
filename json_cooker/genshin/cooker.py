import asyncio
import logging
from typing import Any

import orjson

from ..base import JSONCooker
from ..utils import async_error_handler
from .data import (
    ARTIFACTS,
    CHARACTERS,
    CONSTS,
    FETTER_CHARACTER_CARD_EXCEL,
    LANGS,
    LOC_JSON,
    NAMECARDS,
    REWARD_EXCEL,
    TALENTS,
    TEXT_MAP,
)

LOGGER_ = logging.getLogger(__name__)


class GenshinDeobfuscator:
    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.deobfuscations: dict[str, str] = {}

    def avatarId(self) -> None:
        avatarId = next(
            (
                k
                for k, v in self._data["fetter_character_card"][0].items()
                if len(str(v)) == 8
            ),
            None,
        )
        if avatarId is None:
            raise ValueError("Failed to find avatarId in 'fetter_character_card'")
        self.deobfuscations["avatarId"] = avatarId

    def rewardId(self) -> None:
        rewardId = next(
            (
                k
                for k, v in self._data["fetter_character_card"][0].items()
                if len(str(v)) == 6
            ),
            None,
        )
        if rewardId is None:
            raise ValueError("Failed to find rewardId in 'fetter_character_card'")
        self.deobfuscations["rewardId"] = rewardId

    def rewardItemList(self) -> None:
        rewardItemList = next(
            (k for k, v in self._data["rewards"][0].items() if isinstance(v, list)),
            None,
        )
        if rewardItemList is None:
            raise ValueError("Failed to find rewardItemList in 'rewards'")
        self.deobfuscations["rewardItemList"] = rewardItemList

    def itemId(self) -> None:
        itemId = next(
            (
                k
                for k, v in self._data["rewards"][0][
                    self.deobfuscations["rewardItemList"]
                ][0].items()
                if len(str(v)) == 6
            ),
            None,
        )
        if itemId is None:
            raise ValueError("Failed to find itemId in rewards")
        self.deobfuscations["itemId"] = itemId

    def id(self) -> None:
        id = next(
            (k for k, v in self._data["talents"][0].items() if len(str(v)) == 5), None
        )
        if id is None:
            raise ValueError("Failed to find id in 'talents'")
        self.deobfuscations["id"] = id

    def nameTextMapHash(self) -> None:
        nameTextMapHash = next(
            (
                k
                for talent in self._data["talents"]
                for k, v in talent.items()
                if v == 4051912989
            ),
            None,
        )
        if nameTextMapHash is None:
            raise ValueError("Failed to find nameTextMapHash in 'talents'")
        self.deobfuscations["nameTextMapHash"] = nameTextMapHash

    def skillIcon(self) -> None:
        skillIcon = next(
            (
                k
                for talent in self._data["talents"]
                for k, v in talent.items()
                if v == "Skill_A_01"
            ),
            None,
        )
        if skillIcon is None:
            raise ValueError("Failed to find skillIcon in 'talents'")
        self.deobfuscations["skillIcon"] = skillIcon

    def icon(self) -> None:
        icon = next(
            (
                k
                for const in self._data["consts"]
                for k, v in const.items()
                if v == "UI_Talent_S_Ayaka_01"
            ),
            None,
        )
        if icon is None:
            raise ValueError("Failed to find icon in 'consts'")
        self.deobfuscations["icon"] = icon

    def talentId(self) -> None:
        talentId = next(
            (
                k
                for const in self._data["consts"]
                for k, v in const.items()
                if v == 21
                and const[self.deobfuscations["icon"]] == "UI_Talent_S_Ayaka_01"
            ),
            None,
        )
        if talentId is None:
            raise ValueError("Failed to find talentId in 'consts'")
        self.deobfuscations["talentId"] = talentId

    def deobfuscate(self) -> dict[str, Any]:
        self.avatarId()
        self.rewardId()
        self.rewardItemList()
        self.itemId()
        self.id()
        self.nameTextMapHash()
        self.skillIcon()
        self.icon()
        self.talentId()

        LOGGER_.info("Deobfuscations: %s", self.deobfuscations)

        for k, v in self._data.items():
            str_v = orjson.dumps(v).decode()
            for deobfuscated, obfuscated in self.deobfuscations.items():
                str_v = str_v.replace(obfuscated, deobfuscated)
            self._data[k] = orjson.loads(str_v)

        return self._data


class GenshinJSONCooker(JSONCooker):
    async def _download_files(self) -> None:
        tasks = [
            self._download(LOC_JSON, "loc_json"),
            self._download(ARTIFACTS, "artifacts"),
            self._download(TALENTS, "talents"),
            self._download(CONSTS, "consts"),
            self._download(REWARD_EXCEL, "rewards"),
            self._download(FETTER_CHARACTER_CARD_EXCEL, "fetter_character_card"),
            self._download(NAMECARDS, "namecards"),
            self._download(CHARACTERS, "characters"),
        ]
        for lang in LANGS:
            tasks.append(
                self._download(
                    TEXT_MAP.format(lang=lang),
                    f"text_map_{lang}",
                )
            )
        await asyncio.gather(*tasks)

    @async_error_handler
    async def _cook_text_map(self) -> None:
        loc_json = self._data["loc_json"]

        text_map_hahes: list[int] = [
            artifact["nameTextMapHash"] for artifact in self._data["artifacts"]
        ]
        text_map_hahes.extend(
            [talent["nameTextMapHash"] for talent in self._data["talents"]]
        )
        text_map_hahes.extend(
            [const["nameTextMapHash"] for const in self._data["consts"]]
        )

        for lang, lang_code in LANGS.items():
            text_map = self._data[f"text_map_{lang}"]

            # Add the translated texts to loc.json
            for text_map_hash in text_map_hahes:
                string_tm_hash = str(text_map_hash)
                if string_tm_hash in text_map:
                    loc_json[lang_code][string_tm_hash] = text_map[string_tm_hash]

            await self._save_data(f"text_map_{lang_code}", loc_json[lang_code])

        await self._save_data("text_map", loc_json)

    @async_error_handler
    async def _cook_talents(self) -> None:
        talents = self._data["talents"]
        result: dict[str, Any] = {}

        for talent in talents:
            result[str(talent["id"])] = {
                "nameTextMapHash": talent["nameTextMapHash"],
                "icon": talent.get("skillIcon", ""),
            }

        await self._save_data("talents", result)

    @async_error_handler
    async def _cook_consts(self) -> None:
        consts = self._data["consts"]
        result: dict[str, Any] = {}

        for const in consts:
            result[str(const["talentId"])] = {
                "nameTextMapHash": const["nameTextMapHash"],
                "icon": const["icon"],
            }

        await self._save_data("consts", result)

    @async_error_handler
    async def _cook_characters(self) -> None:
        rewards: list[dict[str, Any]] = self._data["rewards"]
        character_cards: list[dict[str, int]] = self._data["fetter_character_card"]
        namecards: dict[str, dict[str, str]] = self._data["namecards"]
        characters: dict[str, Any] = self._data["characters"]

        for character_card in character_cards:
            if character_card["fetterLevel"] != 10:
                continue

            character_id = character_card["avatarId"]
            for reward in rewards:
                if character_card["rewardId"] == reward["rewardId"]:
                    item_id = reward["rewardItemList"][0]["itemId"]
                    namecard_icon = namecards[str(item_id)]["Icon"]
                    character_data = characters[str(character_id)]
                    character_data["NamecardIcon"] = namecard_icon

        await self._save_data("characters", characters)

    async def cook(self) -> None:
        await self._download_files()

        deobfuscator = GenshinDeobfuscator(self._data)
        self._data = deobfuscator.deobfuscate()
        await self._save_data("deobfuscations", deobfuscator.deobfuscations)

        await self._cook_characters()
        await self._cook_talents()
        await self._cook_consts()
        await self._cook_text_map()

        LOGGER_.info("Done!")
