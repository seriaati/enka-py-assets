import asyncio
from collections import defaultdict
import logging
import re
from typing import Any

from ..base import JSONCooker
from ..utils import async_error_handler
from .data import (
    HSR_JSON,
    LANGS,
    OLD_HSR_JSON,
    PROPERTY_CONFIG,
    RELIC_SET_CONFIG,
    SKILL,
    SKILL_TREE,
    SKILL_TREE_LD,
    TEXT_MAP,
)

LOGGER_ = logging.getLogger(__name__)


class HSRJSONCooker(JSONCooker):
    _game = "hsr"

    async def _download_files(self) -> None:
        tasks = [
            self._download(SKILL, "skill"),
            self._download(SKILL_TREE, "skill_tree"),
            self._download(SKILL_TREE_LD, "skill_tree_ld"),
            self._download(PROPERTY_CONFIG, "property_config"),
            self._download(HSR_JSON, "hsr_json"),
            self._download(OLD_HSR_JSON, "old_hsr_json"),
            self._download(RELIC_SET_CONFIG, "relic_set_config"),
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
    async def _cook_skill(self) -> None:
        skill_tree: list[dict[str, Any]] = self._data["skill_tree"]
        skill: list[dict[str, Any]] = self._data["skill"]

        data: dict[str, dict[str, Any]] = {}
        level_ups: dict[int, list[int]] = defaultdict(list)

        for point in skill_tree:
            level = point["Level"]
            if level != 1:
                continue

            point_id = point["PointID"]
            level_up_skill_ids: list[int] = point["LevelUpSkillID"]
            for skill_id in level_up_skill_ids:
                level_ups[skill_id].append(point_id)

        for s in skill:
            skill_id = str(s["SkillID"])
            data[skill_id] = {
                "name": s["SkillName"]["Hash"],
                "desc": s["SkillDesc"]["Hash"] if "SkillDesc" in s else "",
                "simple_desc": s["SimpleSkillDesc"]["Hash"]
                if "SimpleSkillDesc" in s
                else "",
                "icon": s["SkillIcon"],
                "tag": s["SkillTag"]["Hash"],
                "type_desc": s["SkillTypeDesc"]["Hash"] if "SkillTypeDesc" in s else "",
                "effect": s["SkillEffect"],
            }
            for point_id in level_ups.get(s["SkillID"], []):
                data[str(point_id)] = data[skill_id]

        await self._save_data("hsr/skill", data)

    @async_error_handler
    async def _cook_skill_tree(self) -> None:
        skill_tree: list[dict[str, Any]] = self._data["skill_tree"]
        skill_tree_ld: list[dict[str, Any]] = self._data["skill_tree_ld"]

        data: dict[str, dict[str, Any]] = {}

        for skill in skill_tree + skill_tree_ld:
            skill_id = str(skill["PointID"])
            new_skill_data = data[skill_id] = {}
            new_skill_data["anchor"] = skill["AnchorType"]

            icon_path = re.sub(r"Avatar/(\d+)/", "", skill["IconPath"])
            new_skill_data["icon"] = icon_path
            new_skill_data["pointType"] = skill["PointType"]
            new_skill_data["maxLevel"] = skill["MaxLevel"]

            if skill["StatusAddList"]:
                stat = skill["StatusAddList"][0]
                new_skill_data["addStatus"] = {
                    "type": stat["PropertyType"],
                    "value": stat["Value"]["Value"],
                }

            new_skill_data["skillIds"] = skill["LevelUpSkillID"]

        await self._save_data("hsr/skill_tree", data)

    @async_error_handler
    async def _cook_property_config(self) -> None:
        property_config: list[dict[str, Any]] = self._data["property_config"]

        data: dict[str, str] = {}

        for property in property_config:
            data[property["PropertyType"]] = property["IconPath"]

        await self._save_data("hsr/property_config", data)

    @async_error_handler
    async def _cook_hsr_json(self) -> None:
        # Merge old and new HSR JSONs
        hsr_json = self._data["hsr_json"]
        old_hsr_json = self._data["old_hsr_json"]

        for lang, text_map in old_hsr_json.items():
            hsr_json[lang] = {**hsr_json.get(lang, {}), **text_map}

        text_map_hahes: list[int] = []
        for skill in self._data["skill"]:
            text_map_hahes.append(skill["SkillName"]["Hash"])
            text_map_hahes.append(skill["SkillTag"]["Hash"])
            if "SkillDesc" in skill:
                text_map_hahes.append(skill["SkillDesc"]["Hash"])
            if "SimpleSkillDesc" in skill:
                text_map_hahes.append(skill["SimpleSkillDesc"]["Hash"])
            if "SkillTypeDesc" in skill:
                text_map_hahes.append(skill["SkillTypeDesc"]["Hash"])

        for lang, lang_code in LANGS.items():
            text_map = self._data[f"text_map_{lang}"]

            # Add the translated texts to hsr.json
            for text_map_hash in text_map_hahes:
                string_tm_hash = str(text_map_hash)
                if string_tm_hash in text_map:
                    hsr_json[lang_code][string_tm_hash] = text_map[string_tm_hash]

        await self._save_data("hsr/hsr", hsr_json)

    @async_error_handler
    async def _cook_relic_set_config(self) -> None:
        relic_set_config: list[dict[str, Any]] = self._data["relic_set_config"]

        data: dict[str, dict[str, Any]] = {}

        for relic in relic_set_config:
            set_id = str(relic["SetID"])
            data[set_id] = {
                "name": relic["SetName"]["Hash"],
                "icon": relic["SetIconPath"],
                "set_nums": relic["SetSkillList"],
                "is_planar": relic.get("IsPlanarSuit", False),
            }

        await self._save_data("hsr/relic_set", data)

    async def download(self) -> None:
        await self._download_files()
        await asyncio.gather(*[self._save_raw(name) for name in self._data])

    async def dump(self) -> None:
        if not self._data:
            await self._load_all_raw()

        await self._cook_skill()
        await self._cook_skill_tree()
        await self._cook_property_config()
        await self._cook_hsr_json()
        await self._cook_relic_set_config()

        LOGGER_.info("Done!")

    async def cook(self) -> None:
        await self.download()
        await self.dump()
