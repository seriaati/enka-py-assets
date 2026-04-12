LANGS = {
    "CHS": "zh-cn",
    "CHT": "zh-tw",
    "DE": "de",
    "EN": "en",
    "ES": "es",
    "FR": "fr",
    "ID": "id",
    "JP": "ja",
    "KR_0": "ko",
    "KR_1": "ko",
    "PT": "pt",
    "RU_0": "ru",
    "RU_1": "ru",
    "TH_0": "th",
    "TH_1": "th",
    "VI": "vi",
}

STARRAIL_DATA = "https://gitlab.com/Dimbreath/turnbasedgamedata/-/raw/main"

TEXT_MAP = f"{STARRAIL_DATA}/TextMap/TextMap{{lang}}.json"

SKILL = f"{STARRAIL_DATA}/ExcelOutput/AvatarSkillConfig.json"
SKILL_TREE = f"{STARRAIL_DATA}/ExcelOutput/AvatarSkillTreeConfig.json"
SKILL_TREE_LD = f"{STARRAIL_DATA}/ExcelOutput/AvatarSkillTreeConfigLD.json"
PROPERTY_CONFIG = f"{STARRAIL_DATA}/ExcelOutput/AvatarPropertyConfig.json"
RELIC_SET_CONFIG = f"{STARRAIL_DATA}/ExcelOutput/RelicSetConfig.json"


ENKA_API_DOCS = "https://raw.githubusercontent.com/pizza-studio/EnkaDBGenerator/refs/heads/main/Sources/EnkaDBFiles/Resources/Specimen/HSR"
HSR_JSON = f"{ENKA_API_DOCS}/hsr.json"  # Text map
ELATION_HSR_JSON = "https://raw.githubusercontent.com/seriaati/EnkaDBGenerator/refs/heads/update-specimen-20/Sources/EnkaDBFiles/Resources/Specimen/HSR/hsr.json"

OLD_ENKA_API_DOCS = "https://raw.githubusercontent.com/pizza-studio/EnkaDBGenerator/a68f4783fd9310efdd76ada707d39ca12f2735c6/Sources/EnkaDBFiles/Resources/Specimen/HSR"
OLD_HSR_JSON = f"{OLD_ENKA_API_DOCS}/hsr.json"  # Text map
