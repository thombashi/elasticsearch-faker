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
      --locale [ar_EG|zh_CN|ka_GE|fr_FR|hi_IN|ko_KR|bg_BG|ne_NP|en_CA|nl_NL|ar_PS|en_US|el_GR|tr_TR|lt_LT|de_DE|no_NO|pt_BR|uk_UA|ja_JP|dk_DK|es_ES|pl_PL|sl_SI|it_IT|pt_PT|lv_LV|cs_CZ|fi_FI|fa_IR|hu_HU|ro_RO|en_AU|hr_HR|bs_BA|en_GB|zh_TW|en_NZ|ru_RU|sv_SE|es_MX|ar_SA|et_EE]
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
      --index NAME           Name of an index to create. Defaults to test_index.
      --mapping PATH         Path to a mapping file.
      --template PATH        Path to a faker template file.
      -n, --num-doc INTEGER  Number of generating docs. Using bulk API if the
                             value equals or greater than two. Defaults to 500.
      --bulk-size INTEGER    Number of docs for a single bulk API call. Defaults
                             to 200.
      --delete-index         Delete the index if already exists before generating
                             docs.
      -j, --jobs INTEGER     Number of jobs. Defaults to 1.
      --stdin                Read a faker template from stdin.
      --dry-run              Do no harm.
      -h, --help             Show this message and exit.

      Issue tracker: https://github.com/thombashi/elasticsearch-faker/issues


Dependencies
============================================
- Elasticsearch 7 or newer
- Python 3.5+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/elasticsearch-faker/network/dependencies>`__
