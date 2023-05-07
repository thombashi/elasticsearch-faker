from enum import Enum, unique
from textwrap import dedent


MODULE_NAME = "elasticsearch-faker"
COMMAND_EPILOG = dedent(
    """\
    Issue tracker: https://github.com/thombashi/{}/issues
    """
).format(MODULE_NAME)


@unique
class SchemaSource(Enum):
    FILE = 0
    STDIN = 1


@unique
class Context(Enum):
    LOG_LEVEL = 0
    VERBOSITY_LEVEL = 10
    LOCALE = 20
    SEED = 30
    BASIC_AUTH_USER = 40
    BASIC_AUTH_PASSWORD = 41
    VERIFY_CERTS = 50
    SSL_ASSERT_FINGERPRINT = 51


class Default:
    BULK_SIZE = 200
    INDEX = "test_index"
    NUM_DOC = 1000
    NUM_WORKER = 1
    TIMEOUT = 300
    LOCALE = "en_US"


class Environment:
    BASIC_AUTH_USER = "ES_BASIC_AUTH_USER"
    BASIC_AUTH_PASSWORD = "ES_BASIC_AUTH_PASSWORD"
    SSL_ASSERT_FINGERPRINT = "ES_SSL_ASSERT_FINGERPRINT"
