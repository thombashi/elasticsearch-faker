import pytest
from click.testing import CliRunner

from elasticsearch_faker.__main__ import cmd


class Test_cli:
    @pytest.mark.parametrize(
        ["options", "expected"],
        [
            [["-h"], 0],
            [["version", "-h"], 0],
            [["generate", "-h"], 0],
            [["provider", "-h"], 0],
        ],
    )
    def test_help(self, options, expected):
        runner = CliRunner()
        result = runner.invoke(cmd, options)
        assert result.exit_code == expected
