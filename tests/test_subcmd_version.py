import pytest
from click.testing import CliRunner

from elasticsearch_faker.__main__ import cmd


class Test_version_subcmd:
    @pytest.mark.parametrize(
        ["options", "expected"],
        [
            [["version"], 0],
        ],
    )
    def test_smoke(self, options, expected):
        runner = CliRunner()
        result = runner.invoke(cmd, options)
        assert result.exit_code == expected
        assert len(result.stdout) > 50
