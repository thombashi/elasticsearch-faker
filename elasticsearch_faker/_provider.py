import errno
import inspect
import re
import sys
from difflib import SequenceMatcher
from typing import Dict  # noqa
from typing import AbstractSet, List, Sequence, Tuple

from faker import Factory

from ._logger import logger


re_provider = re.compile(r"{{\s(?P<providers>[a-z_0-9]+)\s+}}")

_not_provider_regexp = re.compile("^(add|del|get|set)_[a-z_]+")
_not_provider_methods = (
    "__init__",
    "_Generator__format_token",
    "format",
    "parse",
    "provider",
    "seed",
)


def _get_valid_providers(locale: str) -> Sequence[str]:
    return tuple(
        method[0]
        for method in inspect.getmembers(Factory.create(locale), inspect.ismethod)
        if _not_provider_regexp.search(method[0]) is None and method[0] not in _not_provider_methods
    )


_provider_cache: Dict[str, AbstractSet] = {}
_valid_locals = (
    "ar_EG",
    "ar_PS",
    "ar_SA",
    "bs_BA",
    "bg_BG",
    "cs_CZ",
    "de_DE",
    "dk_DK",
    "el_GR",
    "en_AU",
    "en_CA",
    "en_GB",
    "en_NZ",
    "en_US",
    "es_ES",
    "es_MX",
    "et_EE",
    "fa_IR",
    "fi_FI",
    "fr_FR",
    "hi_IN",
    "hr_HR",
    "hu_HU",
    "it_IT",
    "ja_JP",
    "ko_KR",
    "lt_LT",
    "lv_LV",
    "ne_NP",
    "nl_NL",
    "no_NO",
    "pl_PL",
    "pt_BR",
    "pt_PT",
    "ro_RO",
    "ru_RU",
    "sl_SI",
    "sv_SE",
    "tr_TR",
    "uk_UA",
    "zh_CN",
    "zh_TW",
    "ka_GE",
)


def check_providers(locale: str, providers: Sequence[str]) -> None:
    if not providers:
        logger.debug("providers not found")
        return

    diffs = set(providers) - get_providers(locale)
    if diffs:
        logger.error(f"invalid providers found: {diffs}")

        for invalid_provider in diffs:
            similar_providers = find_similar_providers(locale, invalid_provider)
            if similar_providers:
                logger.error(
                    "provider not found ({}): might be: {}".format(
                        invalid_provider, ", ".join(similar_providers)
                    )
                )
        sys.exit(errno.EINVAL)


def get_providers(locale: str) -> AbstractSet[str]:
    if locale not in _provider_cache:
        _provider_cache[locale] = frozenset(_get_valid_providers(locale))

    return _provider_cache[locale]


def get_locals() -> Tuple:
    return _valid_locals


def find_similar_providers(locale: str, provider: str) -> List[str]:
    similar_providers = {}

    for avail_provider in get_providers(locale):
        ratio = SequenceMatcher(None, provider, avail_provider).ratio()
        if ratio >= 0.5:
            similar_providers[avail_provider] = ratio

    return [
        pair[0] for pair in sorted(similar_providers.items(), key=lambda x: x[1], reverse=True)[:2]
    ]
