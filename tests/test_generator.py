import json
from textwrap import dedent

from faker import Factory, Faker

from elasticsearch_faker._generator import FakeDocGenerator
from elasticsearch_faker._provider import re_provider


class TestFakeDocGenerator:
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
        output = generator.generate_docs(bulk_size=2)
        print(json.dumps(output, indent=4))
        assert output == [
            {"index": {"_index": "test_index", "_id": "e3e70682-c209-4cac-a29f-6fbed82c07cd"}},
            {
                "name": "David Dixon",
                "address": "75938 Donald Corner Suite 892 Lake Rachel, MS 13700",
            },
            {"index": {"_index": "test_index", "_id": "9c6316b9-50f2-4455-af25-e2a25a921187"}},
            {
                "name": "Christine Tran",
                "address": "80160 Clayton Highway Suite 139 Lake Douglasmouth, WY 67077",
            },
        ]

        output = generator.generate_docs(bulk_size=2)
        print(json.dumps(output, indent=4))
        assert output == [
            {"index": {"_index": "test_index", "_id": "1beb3711-7d41-4602-aece-328bff7b118e"}},
            {
                "name": "Eddie Martinez",
                "address": "98947 Lauren Harbors Apt. 232 Port Jordanton, CT 20102",
            },
            {"index": {"_index": "test_index", "_id": "148b2758-d7ab-4928-89e4-69e6ec62b2c8"}},
            {
                "name": "Tammy Fernandez",
                "address": "33969 Travis Port Suite 515 Tomstad, ID 96378",
            },
        ]
