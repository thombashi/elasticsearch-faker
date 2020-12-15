from click.testing import CliRunner

from elasticsearch_faker.__main__ import cmd


class Test_valiate_subcmd:
    def test_normal(self):
        runner = CliRunner()
        template_filename = "valid.tmpl"

        with runner.isolated_filesystem():
            with open(template_filename, "w") as f:
                f.write(
                    """\
                    {
                        "name": "{{ name }}",
                        "address": "{{ address }}"
                    }
                    """
                )
            result = runner.invoke(cmd, ["validate", template_filename])
            assert result.exit_code == 0

    def test_abnormal(self):
        runner = CliRunner()
        template_filename = "invalid.tmpl"

        with runner.isolated_filesystem():
            with open(template_filename, "w") as f:
                f.write(
                    """\
                    {
                        "name": "{{ name }}",
                        "address": "{{ invalid_provider }}"
                    }
                    """
                )
            result = runner.invoke(cmd, ["validate", template_filename])
            assert result.exit_code != 0
