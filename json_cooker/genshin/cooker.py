import asyncio
import logging
from typing import Any

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
                "icon": talent["skillIcon"],
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
        rewards = self._data["rewards"]
        character_cards = self._data["fetter_character_card"]
        namecards: dict[str, dict[str, str]] = self._data["namecards"]
        characters: dict[str, Any] = self._data["characters"]

        for character_card in character_cards:
            character_id = character_card["avatarId"]
            for reward in rewards:
                if character_card["rewardId"] == reward["rewardId"]:
                    item_id = reward["rewardItemList"][0]["itemId"]
                    namecard_icon = namecards[str(item_id)]["icon"]
                    character_data = characters[str(character_id)]
                    character_data["NamecardIcon"] = namecard_icon

        await self._save_data("characters", characters)

    async def cook(self) -> None:
        await self._download_files()

        await self._cook_characters()
        await self._cook_talents()
        await self._cook_consts()
        await self._cook_text_map()

        LOGGER_.info("Done!")
