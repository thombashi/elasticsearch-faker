.. contents:: **elasticsearch-faker**
   :backlinks: top
   :depth: 2


Summary
============================================
`elasticsearch-faker` is a CLI tool to generate fake data for Elasticsearch.

.. image:: https://github.com/thombashi/elasticsearch-faker/workflows/Tests/badge.svg
    :target: https://github.com/thombashi/elasticsearch-faker/actions?query=workflow%3ATests
    :alt: Linux/macOS/Windows CI status


Installation
============================================
::

    pip install elasticsearch-faker


Usage
============================================

:Sample Code:
    .. code-block:: python

        # Sample code

:Output:
    .. code-block::

        # Output


Command help
----------------------------------------------
::

    Usage: elasticsearch-faker [OPTIONS] COMMAND [ARGS]...

      Faker for Elasticsearch

    Options:
      --version                       Show the version and exit.
      --debug                         For debug print.
      -q, --quiet                     Suppress execution log messages.
      -v, --verbose
      --locale [de_DE|ar_SA|en_GB|hi_IN|en_CA|en_US|zh_CN|es_MX|lv_LV|pl_PL|ar_PS|ko_KR|hr_HR|fr_FR|ne_NP|hu_HU|ru_RU|es_ES|bs_BA|bg_BG|fi_FI|dk_DK|pt_BR|nl_NL|el_GR|zh_TW|ka_GE|fa_IR|cs_CZ|lt_LT|pt_PT|tr_TR|ar_EG|it_IT|ro_RO|sv_SE|uk_UA|et_EE|en_AU|ja_JP|en_NZ|no_NO|sl_SI]
                                      Specify localization for fake data. Defaults
                                      to en_US.

      --seed INTEGER
      -h, --help                      Show this message and exit.

    Commands:
      generate  Generate fake data and put it to Elasticsearch
      provider
      validate  Check that a faker template file is well formed.
      version   Show version information

      Issue tracker: https://github.com/thombashi/elasticsearch-faker/issues

::

    Usage: elasticsearch-faker generate [OPTIONS] HOST

      Generate fake data and put it to Elasticsearch

    Options:
      --index NAME           Path to a faker template file. Defaults to
                             test_index.

      --mapping PATH         Path to a mapping file.
      --template PATH        Path to a faker template file.
      -n, --num-doc INTEGER  Number of generating docs. Using bulk API if the
                             value equals or greater than two. Defaults to 500.

      --bulk-size INTEGER    Number of docs for a single bulk API call. Defaults
                             to 200.

      --delete-index         Delete the index if already exists before generating
                             docs.

      --stdin                Read a faker template from stdin.
      --dry-run              Do no harm.
      -h, --help             Show this message and exit.

      Issue tracker: https://github.com/thombashi/elasticsearch-faker/issues


Dependencies
============================================
- Elasticsearch 7 or newer
- Python 3.5+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/elasticsearch-faker/network/dependencies>`__
