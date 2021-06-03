import json
from typing import Dict

import click
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import JsonLexer


def print_dict(input_dict: Dict, indent=4) -> None:
    click.echo(
        highlight(
            code=json.dumps(input_dict, indent=indent),
            lexer=JsonLexer(),
            formatter=TerminalTrueColorFormatter(style="monokai"),
        ).strip()
    )
