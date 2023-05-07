import copy
import errno
import math
import os
import sys
import time
import warnings
from concurrent import futures
from typing import Optional, Tuple

import click
from elasticsearch.exceptions import ElasticsearchWarning
from faker import Factory, Faker
from tqdm import tqdm

from .__version__ import __version__
from ._const import COMMAND_EPILOG, MODULE_NAME, Context, Default, Environment
from ._es_client import ElasticsearchClientInterface, ElasticsearchClientParameter, create_es_client
from ._generator import FakeDocGenerator
from ._logger import LogLevel, initialize_logger, logger
from ._print import print_dict
from ._provider import get_locals, re_provider
from ._template import check_template
from .subcmd.provider import provider


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], obj={})


def _extract_basic_auth_user(user: Optional[str]) -> Optional[str]:
    if user:
        return user

    return os.getenv(Environment.BASIC_AUTH_USER)


def _extract_basic_auth_password(password: Optional[str]) -> Optional[str]:
    if password:
        return password

    return os.getenv(Environment.BASIC_AUTH_PASSWORD)


def _extract_ssl_assert_fingerprint(fingerprint: Optional[str]) -> Optional[str]:
    if fingerprint:
        return fingerprint

    return os.getenv(Environment.SSL_ASSERT_FINGERPRINT)


def _read_template_text(template_filepath: str, use_stdin: bool) -> str:
    template_text = None

    if not sys.stdin.isatty() and use_stdin:
        logger.debug("read from the stdin")

        template_text = sys.stdin.read()
    elif template_filepath:
        if not os.path.exists(template_filepath):
            logger.error(f"no such file: {template_filepath}")
            sys.exit(errno.ENOENT)

        logger.debug(f"load from a template file: {template_filepath}")

        with open(template_filepath) as f:
            template_text = f.read()

    if not template_text:
        logger.error("require template")
        sys.exit(errno.EINVAL)

    return template_text


def _fetch_store_size_in_bytes(
    es_client: ElasticsearchClientInterface,
    index_name: str,
    min_store_size_in_bytes: int,
    max_wait_secs: float = 10,
) -> int:
    SLEEP_SECS = 0.5
    max_loop = math.ceil(max_wait_secs / SLEEP_SECS)
    store_size_in_bytes = 0

    for i in range(max_loop):
        primaries_stats_after = es_client.fetch_stats(index_name)["primaries"]
        store_size_in_bytes = primaries_stats_after["store"]["size_in_bytes"]

        if store_size_in_bytes >= min_store_size_in_bytes:
            break

        logger.debug(
            f"wait for docs stats to be reflected [{i}/{max_loop}]:"
            f"current={store_size_in_bytes}bytes"
        )

        time.sleep(SLEEP_SECS)

    return store_size_in_bytes


def to_megabytes(size_in_bytes: int) -> float:
    return size_in_bytes / 1024**2


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
    default=Default.LOCALE,
    help=f"Specify localization for fake data. Defaults to {Default.LOCALE}.",
)
@click.option(
    "--seed",
    type=int,
    help="Random seed for faker.",
)
@click.option(
    "--basic-auth-user",
    help=f"""
        User name for Elasticsearch basic authentication.
        Or you can set the value via {Environment.BASIC_AUTH_USER} environment variable.
    """,
)
@click.option(
    "--basic-auth-password",
    help=f"""
        Password for Elasticsearch basic authentication.
        Or you can set the value via {Environment.BASIC_AUTH_PASSWORD} environment variable.
    """,
)
@click.option(
    "--verify-certs",
    is_flag=True,
    help=f"""
        Verify Elasticsearch server certificate.
        Or you can set the value via {Environment.SSL_ASSERT_FINGERPRINT} environment variable.
    """,
)
@click.option(
    "--ssl-assert-fingerprint",
    help="SSL certificate fingerprint to verify.",
)
@click.option("--ignore-es-warn", is_flag=True, default=False, help="Ignore ElasticsearchWarning.")
@click.pass_context
def cmd(
    ctx,
    log_level: str,
    verbosity_level: int,
    locale: str,
    seed: Optional[int],
    basic_auth_user: Optional[str],
    basic_auth_password: Optional[str],
    verify_certs: bool,
    ssl_assert_fingerprint: Optional[str],
    ignore_es_warn: bool,
):
    """
    Faker for Elasticsearch.
    """

    ctx.obj[Context.LOG_LEVEL] = LogLevel.INFO if log_level is None else log_level
    ctx.obj[Context.VERBOSITY_LEVEL] = verbosity_level
    ctx.obj[Context.LOCALE] = locale
    ctx.obj[Context.SEED] = seed
    ctx.obj[Context.BASIC_AUTH_USER] = _extract_basic_auth_user(basic_auth_user)
    ctx.obj[Context.BASIC_AUTH_PASSWORD] = basic_auth_password
    ctx.obj[Context.VERIFY_CERTS] = verify_certs
    ctx.obj[Context.SSL_ASSERT_FINGERPRINT] = ssl_assert_fingerprint

    if ignore_es_warn:
        warnings.simplefilter("ignore", ElasticsearchWarning)

    initialize_logger(name=MODULE_NAME, log_level=ctx.obj[Context.LOG_LEVEL])

    context = copy.deepcopy(ctx.obj)
    del context[Context.BASIC_AUTH_PASSWORD]
    del context[Context.SSL_ASSERT_FINGERPRINT]
    logger.debug(context)


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
def version(ctx):
    """
    Show version information.
    """

    import envinfopy

    click.echo(envinfopy.dumps(["elasticsearch", "Faker", "click", "Jinja2"], "markdown"))


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
@click.argument("endpoint", type=str)
@click.option(
    "--index",
    "index_name",
    metavar="NAME",
    default=Default.INDEX,
    help=f"Name of an index to create. Defaults to '{Default.INDEX}'.",
)
@click.option(
    "--mapping",
    "mapping_filepath",
    type=click.Path(),
    help="""
    Path to a mapping file. See also
    https://www.elastic.co/guide/en/elasticsearch/reference/current/explicit-mapping.html
    """,  # noqa
)
@click.option(
    "--doc-template",
    "--template",
    "template_filepath",
    type=click.Path(),
    help="Path to a faker doc template file.",
)
@click.option(
    "-n",
    "--num-doc",
    "num_doc",
    type=int,
    default=Default.NUM_DOC,
    help="""
        Number of generating documents.
        The command uses bulk API if the value equals or is greater than two.
        Defaults to {}.
    """.format(
        Default.NUM_DOC
    ),
)
@click.option(
    "--bulk-size",
    type=int,
    default=Default.BULK_SIZE,
    help="Number of creating documents for a single bulk API call. Defaults to {}.".format(
        Default.BULK_SIZE
    ),
)
@click.option(
    "--delete-index",
    is_flag=True,
    help="Delete the index if already exists before generating documents.",
)
@click.option(
    "-j",
    "--jobs",
    "num_worker",
    type=int,
    default=1,
    help=f"Number of workers that create docs. Defaults to {Default.NUM_WORKER}.",
)
@click.option("--stdin", "use_stdin", is_flag=True, help="Read a faker doc template from stdin.")
@click.option("--dry-run", is_flag=True, help="Do no harm.")
def generate(
    ctx,
    endpoint: str,
    index_name: str,
    mapping_filepath: str,
    template_filepath: str,
    num_doc: int,
    bulk_size: int,
    delete_index: bool,
    num_worker: int,
    use_stdin: bool,
    dry_run: bool,
):
    """
    Generate fake data and put it to an Elasticsearch index.
    """

    locale = ctx.obj[Context.LOCALE]
    seed = ctx.obj[Context.SEED]
    start_time = time.time()

    logger.debug(
        "endpoint={}, index_name={}, template_filepath={}, num_doc={}, bulk_size={}".format(
            endpoint, index_name, template_filepath, num_doc, bulk_size
        )
    )

    template_text = _read_template_text(template_filepath, use_stdin)

    check_template(locale, template_text)
    providers = re_provider.findall(template_text)

    fake = Factory.create(locale)
    if seed is not None:
        Faker.seed(seed)

    es_client_param = ElasticsearchClientParameter(
        endpoint=endpoint,
        basic_auth_user=ctx.obj[Context.BASIC_AUTH_USER],
        basic_auth_password=_extract_basic_auth_password(ctx.obj[Context.BASIC_AUTH_PASSWORD]),
        verify_certs=ctx.obj[Context.VERIFY_CERTS],
        ssl_assert_fingerprint=_extract_ssl_assert_fingerprint(
            ctx.obj[Context.SSL_ASSERT_FINGERPRINT]
        ),
    )
    es_client = create_es_client(es_client_param, dry_run)

    if delete_index:
        es_client.delete_index(index_name)

    err = es_client.create_index(index_name, mapping_filepath)
    if err != 0:
        sys.exit(err)

    primaries_stats_before = es_client.fetch_stats(index_name)["primaries"]
    org_docs_count = es_client.count_docs(index_name)

    doc_generator = FakeDocGenerator(
        template=template_text,
        providers=providers,
        index_name=index_name,
        fake=fake,
    )

    if num_doc == 1:
        sys.exit(es_client.put(index_name, doc_generator.generate_doc()))

    if num_worker == 1:
        _, gen_doc_count = gen_doc_worker(
            es_client_param=es_client_param,
            dry_run=dry_run,
            doc_generator=doc_generator,
            index_name=index_name,
            num_doc=num_doc,
            bulk_size=bulk_size,
        )
        logger.info(f"generate {gen_doc_count} docs to {index_name}")
    else:
        with futures.ProcessPoolExecutor(num_worker) as executor:
            future_list = []
            worker_num_doc = [(num_doc + i) // num_worker for i in range(num_worker)]

            logger.debug(
                "split documents to distribute document generating workers: {}".format(
                    worker_num_doc
                )
            )

            for worker_id in range(num_worker):
                future_list.append(
                    executor.submit(
                        gen_doc_worker,
                        es_client_param,
                        dry_run,
                        doc_generator,
                        index_name,
                        worker_num_doc[worker_id],
                        bulk_size,
                        worker_id,
                    )
                )

            for future in futures.as_completed(future_list):
                worker_id, gen_doc_count = future.result()
                """
                logger.info(
                    "worker {} completed: generate {} docs to {}".format(
                        worker_id, gen_doc_count, index_name
                    )
                )
                """

    es_client.refresh(index_name=index_name)

    store_size_in_bytes = _fetch_store_size_in_bytes(
        es_client, index_name=index_name, min_store_size_in_bytes=num_doc
    )
    current_store_size_in_mb = to_megabytes(store_size_in_bytes)
    # current_docs_count = primaries_stats_after["docs"]["count"]
    current_docs_count = es_client.count_docs(index_name)
    diff_docs_count = current_docs_count - org_docs_count
    elapse_secs = time.time() - start_time

    click.echo(
        "\n".join(
            [
                "\n[Results]",
                f"target index: {index_name}",
                f"completed in {elapse_secs:,.1f} secs",
                f"current store.size: {current_store_size_in_mb:,.1f} MB",
                f"current docs.count: {current_docs_count:,}",
                "generated store.size: {:,.1f} MB".format(
                    current_store_size_in_mb
                    - to_megabytes(primaries_stats_before["store"]["size_in_bytes"])
                ),
                f"average size[byte]/doc: {math.ceil(store_size_in_bytes / current_docs_count):,}",
                f"generated docs.count: {diff_docs_count:,}",
                f"generated docs/secs: {diff_docs_count / elapse_secs:,.1f}",
                f"bulk size: {bulk_size:,}",
            ]
        )
    )


def gen_doc_worker(
    es_client_param: ElasticsearchClientParameter,
    dry_run: bool,
    doc_generator: FakeDocGenerator,
    index_name: str,
    num_doc: int,
    bulk_size: int,
    worker_id: int = 0,
) -> Tuple[int, int]:
    es_client = create_es_client(es_client_param, dry_run)
    gen_doc_count = 0

    with tqdm(
        desc=f"document generator #{worker_id}",
        total=num_doc,
        unit="docs",
        # position=worker_id + 1,  # currently not using position to avoid display corruption
    ) as pbar:
        while gen_doc_count < num_doc:
            next_bulk_size = min(bulk_size, num_doc - gen_doc_count)
            docs = doc_generator.generate_docs(bulk_size=next_bulk_size, worker_id=worker_id)

            try:
                put_count = es_client.bulk_put(index_name, docs)
            except RuntimeError:
                continue

            if put_count == 0:
                break

            gen_doc_count += put_count
            pbar.update(put_count)

    return (worker_id, gen_doc_count)


@cmd.command(epilog=COMMAND_EPILOG)
@click.argument("template_filepath", type=click.Path(exists=True))
@click.pass_context
def validate(ctx, template_filepath: str):
    """
    Check that a faker doc template file is well formed.
    """

    locale = ctx.obj[Context.LOCALE]

    with open(template_filepath) as f:
        check_template(locale, f.read())

    click.echo(f"Schema file at {template_filepath} is valid.")


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
@click.argument("endpoint", type=str)
@click.option(
    "--index",
    "index_name",
    metavar="NAME",
    default=Default.INDEX,
    help=f"Name of an index to show statistics. Defaults to '{Default.INDEX}'.",
)
def show_stats(ctx, endpoint: str, index_name: str):
    """
    Fetch and show statistics of an index.
    """

    es_client = create_es_client(
        ElasticsearchClientParameter(
            endpoint=endpoint,
            basic_auth_user=ctx.obj[Context.BASIC_AUTH_USER],
            basic_auth_password=_extract_basic_auth_password(ctx.obj[Context.BASIC_AUTH_PASSWORD]),
            verify_certs=ctx.obj[Context.VERIFY_CERTS],
            ssl_assert_fingerprint=_extract_ssl_assert_fingerprint(
                ctx.obj[Context.SSL_ASSERT_FINGERPRINT]
            ),
        ),
        dry_run=False,
    )
    stats = es_client.fetch_stats(index_name)

    try:
        primaries_stats = stats["primaries"]
    except KeyError as e:
        logger.error(e)
        sys.exit(errno.ENOENT)

    print_dict(primaries_stats)


cmd.add_command(provider)
