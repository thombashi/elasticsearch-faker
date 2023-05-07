import re
from typing import List

import click
from faker import Factory, Faker
from faker.exceptions import UnsupportedFeature

from .._const import COMMAND_EPILOG, Context
from .._logger import logger
from .._provider import get_providers


DEFAULT_MAX_DISPLAY_LEN = 64


@click.group(epilog=COMMAND_EPILOG)
def provider():
    """
    Show or search providers for doc templates.
    """


@provider.command()
@click.pass_context
def list(ctx):
    """
    List available providers.
    """

    locale = ctx.obj[Context.LOCALE]

    for provider in sorted(get_providers(locale)):
        click.echo(provider)


@provider.command()
@click.argument("pattern", type=str)
@click.pass_context
def search(ctx, pattern: str):
    """
    Search for providers by pattern.
    """

    locale = ctx.obj[Context.LOCALE]
    regexp = re.compile(pattern, re.IGNORECASE)

    for provider in sorted(get_providers(locale)):
        if regexp.search(provider) is None:
            continue

        click.echo(provider)


@provider.command()
@click.argument("providers", type=str, nargs=-1)
@click.option(
    "--max-len",
    metavar="LENGTH",
    type=int,
    default=DEFAULT_MAX_DISPLAY_LEN,
    help=f"Maximum display length per example. Defaults to {DEFAULT_MAX_DISPLAY_LEN}.",
)
@click.pass_context
def example(ctx, providers: List[str], max_len: int):
    """
    List available providers with examples.
    """

    locale = ctx.obj[Context.LOCALE]
    seed = ctx.obj[Context.SEED]

    fake = Factory.create(locale)
    if seed is not None:
        Faker.seed(seed)

    for provider in sorted(get_providers(locale)):
        try:
            value = getattr(fake, provider)()
        except AttributeError:
            # implemented providers may differ locale to locale
            logger.debug(f"provider not found: locale={locale}, provider={provider}")
            continue
        except (TypeError, UnsupportedFeature) as e:
            logger.warning(f"provider={provider}: {e}")
            continue

        str_value = str(value)
        click.echo(f"{provider} (len={len(str_value)}): {str_value[:max_len]}")
