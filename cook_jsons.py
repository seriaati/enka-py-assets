import asyncio
import logging
from typing import Any

import aiofiles
import aiohttp
import orjson

LANGS = {
    "CHS": "zh-CN",
    "CHT": "zh-TW",
    "DE": "de",
    "EN": "en",
    "ES": "es",
    "FR": "fr",
    "ID": "id",
    "IT": "it",
    "JP": "ja",
    "KR": "ko",
    "PT": "pt",
    "RU": "ru",
    "TH": "th",
    "TR": "tr",
    "VI": "vi",
}
LOC_JSON = (
    "https://raw.githubusercontent.com/EnkaNetwork/API-docs/master/store/loc.json"
)
ARTIFACTS = "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/main/ExcelBinOutput/ReliquaryExcelConfigData.json"
TEXT_MAP = (
    "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/main/TextMap/TextMap{lang}.json"
)
TALENTS = "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/main/ExcelBinOutput/AvatarSkillExcelConfigData.json"
CONSTS = "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/main/ExcelBinOutput/AvatarTalentExcelConfigData.json"

LOGGER_ = logging.getLogger("JSONCooker")


class JSONCooker:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._data: dict[str, Any] = {}

    async def _download(self, url: str, name: str) -> None:
        LOGGER_.info("Downloading from %s ...", url)
        async with self._session.get(url) as resp:
            self._data[name] = orjson.loads(await resp.text(encoding="utf-8"))

    async def _download_files(self) -> None:
        tasks = [
            asyncio.create_task(self._download(LOC_JSON, "loc_json")),
            asyncio.create_task(self._download(ARTIFACTS, "artifacts")),
            asyncio.create_task(self._download(TALENTS, "talents")),
            asyncio.create_task(self._download(CONSTS, "consts")),
        ]
        tasks.extend(
            [
                asyncio.create_task(
                    self._download(TEXT_MAP.format(lang=lang), f"text_map_{lang}")
                )
                for lang in LANGS
            ]
        )
        await asyncio.gather(*tasks)

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
                if text_map_hash in text_map:
                    loc_json[lang_code][text_map_hash] = text_map[str(text_map_hash)]

        # Save the new loc.json
        LOGGER_.info("Saving loc.json...")
        async with aiofiles.open("data/text_map.json", "w", encoding="utf-8") as f:
            bytes_ = orjson.dumps(loc_json)
            await f.write(bytes_.decode())

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

    async def cook(self) -> None:
        await self._download_files()
        await self._cook_text_map()
        await self._cook_talents()
        await self._cook_consts()


async def main() -> None:
    handler = logging.StreamHandler()
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    fmt = logging.Formatter(
        "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(fmt)
    LOGGER_.setLevel(logging.INFO)
    LOGGER_.addHandler(handler)

    async with aiohttp.ClientSession() as session:
        cooker = JSONCooker(session)
        await cooker.cook()

    LOGGER_.info("Done!")


asyncio.run(main())
