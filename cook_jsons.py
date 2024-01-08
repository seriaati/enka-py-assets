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


class JSONCooker:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._data: dict[str, Any] = {}

    async def _download(self, url: str, name: str) -> None:
        logging.info("Downloading from %s ...", url)
        async with self._session.get(url) as resp:
            self._data[name] = orjson.loads(await resp.text(encoding="utf-8"))

    async def _download_files(self) -> None:
        tasks = [
            asyncio.create_task(self._download(LOC_JSON, "loc_json")),
            asyncio.create_task(self._download(ARTIFACTS, "artifacts")),
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

    async def cook(self) -> None:
        await self._download_files()

        loc_json = self._data["loc_json"]

        text_map_hahes: list[str] = []
        for artifact in self._data["artifacts"]:
            text_map_hahes.append(str(artifact["nameTextMapHash"]))
            text_map_hahes.append(str(artifact["descTextMapHash"]))

        for lang, lang_code in LANGS.items():
            text_map = self._data[f"text_map_{lang}"]

            # Add the translated text to loc.json
            for text_map_hash in text_map_hahes:
                if text_map_hash in text_map:
                    loc_json[lang_code][text_map_hash] = text_map[text_map_hash]

        # Save the new loc.json
        logging.info("Saving loc.json...")
        async with aiofiles.open("data/text_map.json", "w", encoding="utf-8") as f:
            bytes_ = orjson.dumps(loc_json)
            await f.write(bytes_.decode())


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    async with aiohttp.ClientSession() as session:
        cooker = JSONCooker(session)
        await cooker.cook()

    logging.info("Done!")


asyncio.run(main())
