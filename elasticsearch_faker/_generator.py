import json
from datetime import datetime
from typing import Any, Dict, List, Sequence

from faker import Factory, Faker

from ._logger import logger
from ._provider import re_provider


class FakeDocGenerator:
    def __init__(
        self,
        providers: Sequence[str],
        template: str,
        index_name: str,
        fake: Faker,
    ) -> None:
        self.__providers = providers
        self.__template = template
        self.__index_name = index_name
        self.__fake = fake

        self.__id_fake = Factory.create()
        self.__first = True

    def generate_doc(self) -> Dict:
        return self.__generate_fake_doc()

    def generate_docs(self, bulk_size: int, worker_id: int) -> List[Dict]:
        docs = []

        for i in range(bulk_size):
            docs.append(
                {
                    "index": {
                        "_index": self.__index_name,
                        "_id": f"{self.__id_fake.uuid4()}-{worker_id}",
                    }
                }
            )
            docs.append(self.__generate_fake_doc())

        return docs

    def __generate_fake_doc(self) -> Dict[str, Any]:
        data = []

        for provider in self.__providers:
            try:
                value = getattr(self.__fake, provider)()
            except AttributeError:
                # implemented providers may differ locale to locale
                logger.debug(f"provider not found: provider={provider}")
                continue

            data.append(self.__postprocess(provider, value))

        stash = "____"
        template = re_provider.sub(stash, self.__template).replace("{", "{{").replace("}", "}}")
        template = template.replace(stash, "{}")

        return json.loads(template.format(*data).replace("\n", " "))

    def __postprocess(self, provider: str, value):
        if isinstance(value, datetime):
            if provider == "date_time":
                return value.strftime("%Y-%m-%dT%H:%M:%S.000+0000")
                # value = value.isoformat()
        elif provider == "text":
            return value.replace("\n", "")

        return value
