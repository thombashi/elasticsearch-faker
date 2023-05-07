.. contents:: **elasticsearch-faker**
   :backlinks: top
   :depth: 2


Summary
============================================
`elasticsearch-faker` is a CLI tool to generate fake data for Elasticsearch.

.. image:: https://badge.fury.io/py/elasticsearch-faker.svg
    :target: https://badge.fury.io/py/elasticsearch-faker
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/elasticsearch-faker.svg
    :target: https://pypi.org/project/elasticsearch-faker
    :alt: Supported Python versions

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
      --seed INTEGER                  Random seed for faker.
      --basic-auth-user TEXT          User name for Elasticsearch basic
                                      authentication. Or you can set the value via
                                      ES_BASIC_AUTH_USER environment variable.
      --basic-auth-password TEXT      Password for Elasticsearch basic
                                      authentication. Or you can set the value via
                                      ES_BASIC_AUTH_PASSWORD environment variable.
      --verify-certs                  Verify Elasticsearch server certificate. Or
                                      you can set the value via
                                      ES_SSL_ASSERT_FINGERPRINT environment
                                      variable.
      --ssl-assert-fingerprint TEXT   SSL certificate fingerprint to verify.
      --ignore-es-warn                Ignore ElasticsearchWarning.
      -h, --help                      Show this message and exit.

    Commands:
      generate    Generate fake data and put it to an Elasticsearch index.
      provider    Show or search providers for doc templates.
      show-stats  Fetch and show statistics of an index.
      validate    Check that a faker doc template file is well formed.
      version     Show version information.

      Issue tracker: https://github.com/thombashi/elasticsearch-faker/issues

::

    Usage: elasticsearch-faker generate [OPTIONS] ENDPOINT

      Generate fake data and put it to an Elasticsearch index.

    Options:
      --index NAME                    Name of an index to create. Defaults to
                                      'test_index'.
      --mapping PATH                  Path to a mapping file. See also https://www
                                      .elastic.co/guide/en/elasticsearch/reference
                                      /current/explicit-mapping.html
      --doc-template, --template PATH
                                      Path to a faker doc template file.
      -n, --num-doc INTEGER           Number of generating documents. The command
                                      uses bulk API if the value equals or is
                                      greater than two. Defaults to 1000.
      --bulk-size INTEGER             Number of creating documents for a single
                                      bulk API call. Defaults to 200.
      --delete-index                  Delete the index if already exists before
                                      generating documents.
      -j, --jobs INTEGER              Number of workers that create docs. Defaults
                                      to 1.
      --stdin                         Read a faker doc template from stdin.
      --dry-run                       Do no harm.
      -h, --help                      Show this message and exit.

      Issue tracker: https://github.com/thombashi/elasticsearch-faker/issues

Execution example
----------------------------------------------

Create 1000 docs to an Elasticsearch index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Execution:
    ::

        $ elasticsearch-faker generate --doc-template doc_template.jinja2 https://localhost:9200 -n 1000
        document generator #0: 100%|█████████████████████| 1000/1000 [00:01<00:00, 590.53docs/s]
        [INFO] generate 1000 docs to test_index

        [Results]
        target index: test_index
        completed in 10.4 secs
        current store.size: 3.0 MB
        current docs.count: 1,000
        generated store.size: 3.0 MB
        average size[byte]/doc: 3,164
        generated docs.count: 1,000
        generated docs/secs: 96.3
        bulk size: 200
        $ curl -sS localhost:9200/test_index/_search | jq .hits.hits[:2]
        [
          {
            "_index": "test_index",
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

``{{ XXX }}`` in the template file indicates the used providers of Faker to generate data.
The available providers can be listed by ``elasticsearch-faker provider list`` / ``elasticsearch-faker provider example`` subcommands.

Use Elasticsearch authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Execution:
    ::

      $ export ES_BASIC_AUTH_USER=elastic
      $ export ES_BASIC_AUTH_PASSWORD=<PASSWORD>
      $ export ES_SSL_ASSERT_FINGERPRINT=<HTTP CA certificate SHA-256 fingerprint>

      $ elasticsearch-faker --verify-certs generate --doc-template doc_template.jinja2 https://localhost:9200 -n 1000
      [INFO] generate 1000 docs to test_index

      [Results]
      target index: test_index
      completed in 0.7 secs
      current store.size: 3.9 MB
      current docs.count: 6,000
      generated store.size: 0.0 MB
      average size[byte]/doc: 690
      generated docs.count: 1,000
      generated docs/secs: 1,338.6
      bulk size: 200

      $ curl --insecure -sS https://${ES_BASIC_AUTH_USER}:${ES_BASIC_AUTH_PASSWORD}@localhost:9200/test_index/_search | jq .hits.hits[:2]
      [
        {
          "_index": "test_index",
          "_id": "8PMd9ocBtCWmUGxHBM9L",
          "_score": 1,
          "_source": {
            "name": "lclarke",
            "userId": 331837,
            "createdAt": "1980-07-18T23:42:30.000+0000",
            "body": "Large address animal husband present. In act call animal.Yes plant pressure year me.",
            "ext": "series",
            "blobId": "ede46099-ac97-4447-b86b-0a87ef0180f1"
          }
        },
        {
          "_index": "test_index",
          "_id": "71b76118-91fa-4ed3-a1e0-305694b3d34d-0",
          "_score": 1,
          "_source": {
            "name": "shawnyoder",
            "userId": 80039293,
            "createdAt": "1972-09-28T19:04:31.000+0000",
            "body": "Book television political surface fill position security itself. Not man support attorney attorney which amount finish. Ground mother board natural wait about lot.",
            "ext": "before",
            "blobId": "8913b0a4-dd44-442a-8961-a6be87eb68a6"
          }
        }
      ]

Or without ``--verify-certs`` option:

:Execution:
    ::

      $ export ES_BASIC_AUTH_USER=elastic
      $ export ES_BASIC_AUTH_PASSWORD=<PASSWORD>

      $ elasticsearch-faker generate --doc-template doc_template.jinja2 https://localhost:9200 -n 1000


Dependencies
============================================
- Elasticsearch 8 or newer
- Python 3.7+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/elasticsearch-faker/network/dependencies>`__
