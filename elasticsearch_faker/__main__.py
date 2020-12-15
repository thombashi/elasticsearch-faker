#!/usr/bin/env python3

import errno
import json
import sys
import time

import click
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError
from faker import Factory, Faker
from tqdm import tqdm

from .__version__ import __version__
from ._const import COMMAND_EPILOG, MODULE_NAME, Context, Default
from ._es_client import create_es_client
from ._generator import FakeDocGenerator
from ._logger import LogLevel, initialize_logger, logger
from ._provider import get_locals, re_provider
from ._template import check_template
from .subcmd.provider import provider


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], obj={})


def _read_template_text(template_filepath: str, use_stdin: bool) -> str:
    template_text = None

    if not sys.stdin.isatty() and use_stdin:
        logger.debug("read from the stdin")

        template_text = sys.stdin.read()
    elif template_filepath:
        logger.debug("load from a template file: {}".format(template_filepath))

        with open(template_filepath) as f:
            template_text = f.read()

    if not template_text:
        logger.error("require template")
        sys.exit(errno.EINVAL)

    return template_text


def _create_index(es: Elasticsearch, index_name: str, mapping_filepath: str) -> None:
    if not mapping_filepath:
        return

    with open(mapping_filepath) as f:
        mappings = json.load(f)

    try:
        result = es.indices.create(index=index_name, body=mappings)
        logger.debug(result)
    except TransportError as e:
        if e.error == "resource_already_exists_exception":
            # ignore already existing index
            logger.debug(e)
        else:
            raise


@click.group(context_settings=CONTEXT_SETTINGS, epilog=COMMAND_EPILOG)
@click.version_option(version=__version__, message="%(prog)s %(version)s")
@click.option("--debug", "log_level", flag_value=LogLevel.DEBUG, help="For debug print.")
@click.option(
    "-q",
    "--quiet",
    "log_level",
    flag_value=LogLevel.QUIET,
    help="Suppress execution log messages.",
)
@click.option("-v", "--verbose", "verbosity_level", count=True)
@click.option(
    "--locale",
    type=click.Choice(get_locals()),
    default="en_US",
    help="Specify localization for fake data. Defaults to en_US.",
)
@click.option(
    "--seed",
    type=int,
    help="",
)
@click.pass_context
def cmd(ctx, log_level, verbosity_level, locale, seed):
    """
    Faker for Elasticsearch
    """

    ctx.obj[Context.LOG_LEVEL] = LogLevel.INFO if log_level is None else log_level
    ctx.obj[Context.VERBOSITY_LEVEL] = verbosity_level
    ctx.obj[Context.LOCALE] = locale
    ctx.obj[Context.SEED] = seed

    initialize_logger(name=MODULE_NAME, log_level=ctx.obj[Context.LOG_LEVEL])
    logger.debug(ctx.obj)


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
def version(ctx):
    """
    Show version information
    """

    import envinfopy

    click.echo(envinfopy.dumps(["elasticsearch", "Faker", "click", "Jinja2"], "markdown"))


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
@click.argument("host", type=str)
@click.option(
    "--index",
    "index_name",
    metavar="NAME",
    default=Default.INDEX,
    help="Path to a faker template file. Defaults to {}.".format(Default.INDEX),
)
@click.option("--mapping", "mapping_filepath", type=click.Path(), help="Path to a mapping file.")
@click.option(
    "--template", "template_filepath", type=click.Path(), help="Path to a faker template file."
)
@click.option(
    "-n",
    "--num-doc",
    "num_doc",
    type=int,
    default=Default.NUM_DOC,
    help="""
        Number of generating docs. Using bulk API if the value equals or greater than two.
        Defaults to {}.
    """.format(
        Default.NUM_DOC
    ),
)
@click.option(
    "--bulk-size",
    type=int,
    default=Default.BULK_SIZE,
    help="Number of docs for a single bulk API call. Defaults to {}.".format(Default.BULK_SIZE),
)
@click.option(
    "--delete-index",
    is_flag=True,
    help="Delete the index if already exists before generating docs.",
)
@click.option("--stdin", "use_stdin", is_flag=True, help="Read a faker template from stdin.")
@click.option("--dry-run", is_flag=True, help="Do no harm.")
def generate(
    ctx,
    host,
    index_name,
    mapping_filepath,
    template_filepath,
    num_doc,
    bulk_size,
    delete_index,
    use_stdin,
    dry_run,
):
    """
    Generate fake data and put it to Elasticsearch
    """

    locale = ctx.obj[Context.LOCALE]
    seed = ctx.obj[Context.SEED]
    verbosity_level = ctx.obj[Context.VERBOSITY_LEVEL]
    start_time = time.time()

    logger.debug(
        "host={}, index_name={}, template_filepath={}, num_doc={}, bulk_size={}".format(
            host, index_name, template_filepath, num_doc, bulk_size
        )
    )

    template_text = _read_template_text(template_filepath, use_stdin)

    check_template(locale, template_text)
    providers = re_provider.findall(template_text)

    fake = Factory.create(locale)
    if seed is not None:
        Faker.seed(seed)

    es_client = create_es_client(host, dry_run)

    if delete_index:
        es_client.delete_index(index_name)

    es_client.create_index(index_name, mapping_filepath)

    doc_generator = FakeDocGenerator(
        template=template_text,
        providers=providers,
        index_name=index_name,
        fake=fake,
    )

    if num_doc == 1:
        sys.exit(es_client.put(index_name, doc_generator.generate_doc()))

    gen_count = 0

    with tqdm(desc="generate docs", total=num_doc, unit="docs") as pbar:
        while gen_count < num_doc:
            next_bulk_size = min(bulk_size, num_doc - gen_count)
            docs = doc_generator.generate_docs(bulk_size=next_bulk_size)

            try:
                put_count = es_client.bulk_put(index_name, docs)
            except RuntimeError:
                continue

            if put_count == 0:
                break

            gen_count += put_count
            pbar.update(put_count)

    es_client.refresh(index_name=index_name)

    logger.info("generate {} docs to {}".format(gen_count, index_name))
    # logger.info("docs.count: {}".format(stats["docs"]["count"]))
    logger.info("completed in {:.1f} secs".format(time.time() - start_time))

    stats = es_client.fetch_stats(index_name)
    if "indices" in stats:
        stats = stats["indices"][index_name]["total"]
        logger.info("store.size: {:.1f} KB".format(stats["store"]["size_in_bytes"] / 1024))


@cmd.command(epilog=COMMAND_EPILOG)
@click.argument("template_filepath", type=click.Path(exists=True))
@click.pass_context
def validate(ctx, template_filepath):
    """
    Check that a faker template file is well formed.
    """

    locale = ctx.obj[Context.LOCALE]

    with open(template_filepath) as f:
        check_template(locale, f.read())

    click.echo("Schema file at {} is valid.".format(template_filepath))


cmd.add_command(provider)
