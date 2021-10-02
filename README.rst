.. contents:: **elasticsearch-faker**
   :backlinks: top
   :depth: 2


Summary
============================================
`elasticsearch-faker` is a CLI tool to generate fake data for Elasticsearch.

.. image:: https://badge.fury.io/py/elasticsearch-faker.svg
    :target: https://badge.fury.io/py/elasticsearch-faker
    :alt: PyPI package version

.. image:: https://github.com/thombashi/elasticsearch-faker/workflows/Tests/badge.svg
    :target: https://github.com/thombashi/elasticsearch-faker/actions?query=workflow%3ATests
    :alt: Tests CI status

.. image:: https://github.com/thombashi/elasticsearch-faker/actions/workflows/build_and_release.yml/badge.svg
    :target: https://github.com/thombashi/elasticsearch-faker/actions/workflows/build_and_release.yml
    :alt: Build and release CI status

.. image:: https://github.com/thombashi/elasticsearch-faker/actions/workflows/codeql-analysis.yml/badge.svg
    :target: https://github.com/thombashi/elasticsearch-faker/actions/workflows/codeql-analysis.yml
    :alt: CodeQL


Installation
============================================

Installation: pip
------------------------------
::

    pip install elasticsearch-faker

Installation: dpkg (Ubuntu)
--------------------------------------------

1. Navigate to `Releases page <https://github.com/thombashi/elasticsearch-faker/releases>`__
2. Download the latest ``deb`` package
3. Install with ``dpkg -i`` command


Usage
============================================


Command help
----------------------------------------------
::

    Usage: elasticsearch-faker [OPTIONS] COMMAND [ARGS]...

      Faker for Elasticsearch

    Options:
      --version                       Show the version and exit.
      --debug                         For debug print.
      -q, --quiet                     Suppress execution log messages.
      -v, --verbose                   [x>=0]
      --locale [ar_EG|ar_PS|ar_SA|bs_BA|bg_BG|cs_CZ|de_DE|dk_DK|el_GR|en_AU|en_CA|en_GB|en_NZ|en_US|es_ES|es_MX|et_EE|fa_IR|fi_FI|fr_FR|hi_IN|hr_HR|hu_HU|it_IT|ja_JP|ko_KR|lt_LT|lv_LV|ne_NP|nl_NL|no_NO|pl_PL|pt_BR|pt_PT|ro_RO|ru_RU|sl_SI|sv_SE|tr_TR|uk_UA|zh_CN|zh_TW|ka_GE]
                                      Specify localization for fake data. Defaults
                                      to en_US.
      --seed INTEGER
      -h, --help                      Show this message and exit.

    Commands:
      generate    Generate fake data and put it to Elasticsearch
      provider
      show-stats
      validate    Check that a faker template file is well formed.
      version     Show version information

      Issue tracker: https://github.com/thombashi/elasticsearch-faker/issues

::

    Usage: elasticsearch-faker generate [OPTIONS] HOST

      Generate fake data and put it to Elasticsearch

    Options:
      --index NAME           Name of an index to create. Defaults to 'test_index'.
      --mapping PATH         Path to a mapping file.
      --template PATH        Path to a faker template file.
      -n, --num-doc INTEGER  Number of generating documents. Using bulk API if the
                             value equals or greater than two. Defaults to 1000.
      --bulk-size INTEGER    Number of creating documents for a single bulk API
                             call. Defaults to 200.
      --delete-index         Delete the index if already exists before generating
                             documents.
      -j, --jobs INTEGER     Number of jobs. Defaults to 1.
      --stdin                Read a faker template from stdin.
      --dry-run              Do no harm.
      -h, --help             Show this message and exit.

      Issue tracker: https://github.com/thombashi/elasticsearch-faker/issues


Dependencies
============================================
- Elasticsearch 7 or newer
- Python 3.6+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/elasticsearch-faker/network/dependencies>`__
