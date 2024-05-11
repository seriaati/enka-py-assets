import asyncio
import logging
from typing import Any

import aiofiles
import aiohttp
import orjson

from json_cooker.utils import async_error_handler

from .data import (
    ANIME_GAME_DATA,
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

LOGGER_ = logging.getLogger("JSONCooker")


class GenshinJSONCooker:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._data: dict[str, Any] = {}

    @async_error_handler
    async def _download(self, url: str, name: str) -> None:
        LOGGER_.info("Downloading %s from %s", name, url)
        async with self._session.get(url) as resp:
            self._data[name] = orjson.loads(await resp.text(encoding="utf-8"))

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
                    TEXT_MAP.format(ANIME_GAME_DATA=ANIME_GAME_DATA, lang=lang),
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

        # Save the new loc.json
        LOGGER_.info("Saving loc.json...")
        async with aiofiles.open("data/text_map.json", "w", encoding="utf-8") as f:
            bytes_ = orjson.dumps(loc_json)
            await f.write(bytes_.decode())

    @async_error_handler
    async def _cook_talents(self) -> None:
        talents = self._data["talents"]
        result: dict[str, Any] = {}

        for talent in talents:
            result[str(talent["id"])] = {
                "nameTextMapHash": talent["nameTextMapHash"],
                "icon": talent["skillIcon"],
            }

        LOGGER_.info("Saving talents.json...")
        async with aiofiles.open("data/talents.json", "w", encoding="utf-8") as f:
            bytes_ = orjson.dumps(result)
            await f.write(bytes_.decode())

    @async_error_handler
    async def _cook_consts(self) -> None:
        consts = self._data["consts"]
        result: dict[str, Any] = {}

        for const in consts:
            result[str(const["talentId"])] = {
                "nameTextMapHash": const["nameTextMapHash"],
                "icon": const["icon"],
            }

        LOGGER_.info("Saving consts.json...")
        async with aiofiles.open("data/consts.json", "w", encoding="utf-8") as f:
            bytes_ = orjson.dumps(result)
            await f.write(bytes_.decode())

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

        LOGGER_.info("Saving characters.json...")
        async with aiofiles.open("data/characters.json", "w", encoding="utf-8") as f:
            bytes_ = orjson.dumps(characters)
            await f.write(bytes_.decode())

    async def cook(self) -> None:
        await self._download_files()
        await self._cook_characters()
        await self._cook_talents()
        await self._cook_consts()
        await self._cook_text_map()

        LOGGER_.info("Done!")
