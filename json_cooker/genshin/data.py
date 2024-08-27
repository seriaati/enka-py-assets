from typing import Final

LANGS: Final[dict[str, str]] = {
    "CHS": "zh-cn",
    "CHT": "zh-tw",
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
ENKA_API_DOCS: Final[str] = (
    "https://raw.githubusercontent.com/pizza-studio/EnkaDBGenerator/main/Sources/EnkaDBFiles/Resources/Specimen/GI"
)
ANIME_GAME_DATA: Final[str] = "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master"

LOC_JSON: Final[str] = f"{ENKA_API_DOCS}/loc.json"
NAMECARDS: Final[str] = f"{ENKA_API_DOCS}/namecards.json"
CHARACTERS: Final[str] = f"{ENKA_API_DOCS}/characters.json"

ARTIFACTS: Final[str] = (
    f"{ANIME_GAME_DATA}/ExcelBinOutput/ReliquaryExcelConfigData.json"
)
TEXT_MAP: Final[str] = "{ANIME_GAME_DATA}/TextMap/TextMap{lang}.json"
TALENTS: Final[str] = (
    f"{ANIME_GAME_DATA}/ExcelBinOutput/AvatarSkillExcelConfigData.json"
)
CONSTS: Final[str] = (
    f"{ANIME_GAME_DATA}/ExcelBinOutput/AvatarTalentExcelConfigData.json"
)
REWARD_EXCEL: Final[str] = (
    f"{ANIME_GAME_DATA}/ExcelBinOutput/RewardExcelConfigData.json"
)
FETTER_CHARACTER_CARD_EXCEL: Final[str] = (
    f"{ANIME_GAME_DATA}/ExcelBinOutput/FetterCharacterCardExcelConfigData.json"
)
