import asyncio
import logging
from typing import Any

from ..base import JSONCooker
from ..utils import async_error_handler
from .data import AVATAR_PROMOTION, SKILL_TREE

LOGGER_ = logging.getLogger(__name__)


class HSRJSONCooker(JSONCooker):
    async def _download_files(self) -> None:
        tasks = [
            self._download(SKILL_TREE, "skill_tree"),
            self._download(AVATAR_PROMOTION, "promotions"),
        ]

        await asyncio.gather(*tasks)

    @async_error_handler
    async def _cook_skill_tree(self) -> None:
        skill_tree: dict[str, dict[str, dict[str, Any]]] = self._data["skill_tree"]

        data: dict[str, dict[str, Any]] = {}

        for skill_id, skill_infos in skill_tree.items():
            new_skill_data = data[skill_id] = {}
            skill_info = skill_infos["1"]

            chara_id = skill_info["AvatarID"]

            new_skill_data["anchor"] = skill_info["Anchor"]
            new_skill_data["icon"] = skill_info["IconPath"].replace(
                f"/{chara_id}/", "/"
            )
            new_skill_data["pointType"] = skill_info["PointType"]
            new_skill_data["maxLevel"] = skill_info["MaxLevel"]

            if skill_info["StatusAddList"]:
                stat = skill_info["StatusAddList"][0]
                new_skill_data["addStatus"] = {
                    "type": stat["PropertyType"],
                    "value": stat["Value"]["Value"],
                }

        await self._save_data("hsr/skill_tree", data)

    async def cook(self) -> None:
        await self._download_files()

        await self._cook_skill_tree()

        LOGGER_.info("Done!")
