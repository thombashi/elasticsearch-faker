import errno
import sys
import traceback

from ._logger import logger
from ._provider import check_providers, re_provider


def check_template(locale: str, template_text: str) -> None:
    from jinja2 import Environment
    from jinja2.exceptions import TemplateSyntaxError

    try:
        Environment().parse(template_text)
    except TemplateSyntaxError as e:
        logger.error(e)
        logger.error(traceback.format_tb(e.__traceback__)[-1])
        sys.exit(errno.EINVAL)

    providers = re_provider.findall(template_text)
    logger.debug(f"found providers in the template: {providers}")

    check_providers(locale, providers)
