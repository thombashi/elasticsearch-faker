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

Installation: pip (for Elasticsearch 7)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    pip install elasticsearch-faker[es7]

Installation: pip (for Elasticsearch 8)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    pip install elasticsearch-faker[es8]

Installation: dpkg (Ubuntu)
--------------------------------------------

1. Navigate to `Releases page <https://github.com/thombashi/elasticsearch-faker/releases>`__
2. Download the latest ``deb`` package
3. Install with ``dpkg -i`` command

Installation: Docker container
--------------------------------------------
`Packages page <https://github.com/thombashi/elasticsearch-faker/pkgs/container/elasticsearch-faker>`__


Usage
============================================

Command help
----------------------------------------------
::

    Usage: elasticsearch-faker [OPTIONS] COMMAND [ARGS]...

      Faker for Elasticsearch.

    Options:
      --version                       Show the version and exit.
      --debug                         For debug print.
      -q, --quiet                     Suppress execution log messages.
      -v, --verbose
      --locale [ar_EG|ar_PS|ar_SA|bs_BA|bg_BG|cs_CZ|de_DE|dk_DK|el_GR|en_AU|en_CA|en_GB|en_NZ|en_US|es_ES|es_MX|et_EE|fa_IR|fi_FI|fr_FR|hi_IN|hr_HR|hu_HU|it_IT|ja_JP|ko_KR|lt_LT|lv_LV|ne_NP|nl_NL|no_NO|pl_PL|pt_BR|pt_PT|ro_RO|ru_RU|sl_SI|sv_SE|tr_TR|uk_UA|zh_CN|zh_TW|ka_GE]
                                      Specify localization for fake data. Defaults
                                      to en_US.
      --seed INTEGER
      -h, --help                      Show this message and exit.

    Commands:
      generate    Generate fake data and put it to an Elasticsearch index.
      provider    Show or search providers for template.
      show-stats  Fetch and show statistics of an index.
      validate    Check that a faker template file is well formed.
      version     Show version information.

      Issue tracker: https://github.com/thombashi/elasticsearch-faker/issues

::

    Usage: elasticsearch-faker generate [OPTIONS] ENDPOINT

      Generate fake data and put it to an Elasticsearch index.

    Options:
      --index NAME           Name of an index to create. Defaults to 'test_index'.
      --mapping PATH         Path to a mapping file. See also https://www.elastic.
                             co/guide/en/elasticsearch/reference/current/explicit-
                             mapping.html
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

Execution example
----------------------------------------------
Create 1000 docs to an index:

:Execution:
    ::

        $ elasticsearch-faker generate --template doc_template.jinja2 localhost:9200 -n 1000
        document generator #0: 100%|█████████████████████| 1000/1000 [00:01<00:00, 590.53docs/s]
        [INFO] generate 1000 docs to test_index

        [Results]
        target index: test_index
        completed in 2.5 secs
        current store.size: 0.0 MB
        current docs.count: 1,000
        generated store.size: 0.0 MB
        generated docs.count: 1,000
        generated docs/secs: 395.3
        bulk size: 200
        $ curl -sS localhost:9200/test_index/_search | jq .hits.hits[:2]
        [
          {
            "_index": "test_index",
            "_type": "_doc",
            "_id": "4bdd73c0-7744-4c6f-9736-50e3e8515f1c-0",
            "_score": 1,
            "_source": {
              "name": "jennifer17",
              "userId": 56561230,
              "createdAt": "2009-07-17T06:31:04.000+0000",
              "body": "Present blue happen thus miss toward. Itself race so successful build real beyond score. Look different she receive.Compare miss federal lawyer. Herself prevent approach east.",
              "ext": "course",
              "blobId": "c35769a9-3468-43fc-93c7-3c2f27ec9f64"
            }
          },
          {
            "_index": "test_index",
            "_type": "_doc",
            "_id": "88238d96-5ecc-4639-bb8f-c3f816027560-0",
            "_score": 1,
            "_source": {
              "name": "dnicholson",
              "userId": 457,
              "createdAt": "2008-08-29T22:14:43.000+0000",
              "body": "I sit another health president bring. Very expect international television job parent into.Authority read few stock. International hope yard left measure.Player them get move.",
              "ext": "trial",
              "blobId": "e43faf58-9b66-4a43-b1b7-7540b3996cde"
            }
          }
        ]
:doc template file (doc_template.jinja2):
    .. code-block:: jinja

        {
          "name": "{{ user_name }}",
          "userId": {{ random_number }},
          "createdAt": "{{ date_time }}",
          "body": "{{ text }}",
          "ext": "{{ word }}",
          "blobId": "{{ uuid4 }}"
        }

``{{ XXX }}`` used in the template file is called provider.
The available providers can be listed by ``elasticsearch-faker provider list`` / ``elasticsearch-faker provider example`` subcommands.


Dependencies
============================================
- Elasticsearch 7 or newer
- Python 3.6+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/elasticsearch-faker/network/dependencies>`__
