import json
import sys
from textwrap import dedent

import pytest
from faker import Factory, Faker

from elasticsearch_faker._generator import FakeDocGenerator
from elasticsearch_faker._provider import re_provider


class TestFakeDocGenerator:
    @pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
    def test_normal_generate_docs(self):
        fake = Factory.create()
        Faker.seed(0)

        template_text = dedent(
            """\
            {
                "name": "{{ name }}",
                "address": "{{ address }}"
            }
            """
        )
        providers = re_provider.findall(template_text)

        generator = FakeDocGenerator(
            template=template_text,
            providers=providers,
            index_name="test_index",
            fake=fake,
        )
        output = generator.generate_docs(bulk_size=2, worker_id=0)
        print(json.dumps(output, indent=4))
        assert output == [
            {
                "index": {
                    "_index": "test_index",
                    "_id": "e3e70682-c209-4cac-a29f-6fbed82c07cd-0",
                },
            },
            {
                "name": "David Dixon",
                "address": "5938 Juan Throughway Apt. 948 West Corey, TX 43780",
            },
            {
                "index": {
                    "_index": "test_index",
                    "_id": "5a921187-19c7-4df4-8f4f-f31e78de5857-0",
                }
            },
            {
                "name": "Levi Durham",
                "address": "Unit 7784 Box 0801 DPO AP 52775",
            },
        ]

        output = generator.generate_docs(bulk_size=2, worker_id=0)
        print(json.dumps(output, indent=4))
        assert output == [
            {
                "index": {
                    "_index": "test_index",
                    "_id": "ab0c1681-c8f8-43d0-9329-0a4cb5d32b16-0",
                }
            },
            {
                "name": "Lisa Clayton",
                "address": "139 John Divide Suite 115 Rodriguezside, VT 16860",
            },
            {
                "index": {
                    "_index": "test_index",
                    "_id": "ec188efb-d080-466e-952f-233a8c25166a-0",
                }
            },
            {
                "name": "Tracey Morrison",
                "address": "96593 White View Apt. 094 Jonesberg, FL 05565",
            },
        ]
