import asyncio
import logging
from typing import Any

from ..base import JSONCooker
from ..utils import async_error_handler
from .data import PROPERTY_CONFIG, SKILL_TREE

LOGGER_ = logging.getLogger(__name__)


class HSRJSONCooker(JSONCooker):
    async def _download_files(self) -> None:
        tasks = [
            self._download(SKILL_TREE, "skill_tree"),
            self._download(PROPERTY_CONFIG, "property_config"),
        ]

        await asyncio.gather(*tasks)

    @async_error_handler
    async def _cook_skill_tree(self) -> None:
        skill_tree: list[dict[str, Any]] = self._data["skill_tree"]

        data: dict[str, dict[str, Any]] = {}

        for skill in skill_tree:
            skill_id = str(skill["PointID"])
            new_skill_data = data[skill_id] = {}

            chara_id = skill["AvatarID"]

            new_skill_data["anchor"] = skill["Anchor"]

            # Female trailblazer uses male trailbalzer's icon internally,
            # Male trailblazer's ID is female trailblazer's ID - 1
            icon_path = (
                skill["IconPath"]
                .replace(f"/{chara_id}/", "/")
                .replace(f"/{chara_id-1}/", "/")
            )
            # Adapt to new format while keeping compatibility
            icon_path = icon_path.replace("Avatar/", "")
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

    async def cook(self) -> None:
        await self._download_files()

        await self._cook_skill_tree()
        await self._cook_property_config()

        LOGGER_.info("Done!")
