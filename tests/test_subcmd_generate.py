import sys

import pytest
from click.testing import CliRunner

from elasticsearch_faker.__main__ import cmd


class Test_generate_subcmd:
    @pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
    def test_normal(self, mocker):
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

            bulk_put = mocker.patch(
                "elasticsearch_faker._es_client.NullElasticsearchClient.bulk_put"
            )
            generate_docs = mocker.patch(
                "elasticsearch_faker._generator.FakeDocGenerator.generate_docs"
            )
            options = [
                "--debug",
                "generate",
                "loalhost:9200",
                "--template",
                template_filename,
                "-n",
                900,
                "--bulk-size",
                200,
                "--dry-run",
            ]
            result = runner.invoke(cmd, options)

            print(" ".join(str(opt) for opt in options), file=sys.stderr)
            print(result.stdout)
            bulk_put.assert_called_once()
            generate_docs.assert_called_once_with(bulk_size=200, worker_id=0)
