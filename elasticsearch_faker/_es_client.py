import abc
import errno
import json
import os
import sys
from typing import Dict, List

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError, TransportError

from ._const import Default
from ._logger import logger


class ElasticsearchClientInterface(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def create_index(self, index_name: str, mapping_filepath: str) -> None:
        pass

    @abc.abstractclassmethod
    def delete_index(self, index_name: str) -> None:
        pass

    @abc.abstractclassmethod
    def put(self, index_name: str, doc: Dict) -> int:
        pass

    @abc.abstractclassmethod
    def bulk_put(self, index_name: str, docs: List[Dict]) -> int:
        pass

    @abc.abstractclassmethod
    def refresh(self, index_name: str) -> None:
        pass


class NullElasticsearchClient(ElasticsearchClientInterface):
    def create_index(self, index_name: str, mapping_filepath: str) -> None:
        logger.debug("create index: {}".format(index_name))

    def delete_index(self, index_name: str) -> None:
        logger.debug("delete index: {}".format(index_name))

    def put(self, index_name: str, doc: Dict) -> int:
        logger.debug("put a doc to {}".format(index_name))
        print(json.dumps(doc, indent=4))
        return 0

    def bulk_put(self, index_name: str, docs: List[Dict]) -> int:
        num_docs = len(docs) // 2
        logger.debug("put {} docs to {}".format(num_docs, index_name))
        print(json.dumps(docs, indent=4))
        return num_docs

    def refresh(self, index_name: str) -> None:
        logger.debug("refresh {}".format(index_name))

    def fetch_stats(self, index_name: str) -> Dict:
        return {}


class ElasticsearchClient(ElasticsearchClientInterface):
    def __init__(self, es: Elasticsearch) -> None:
        self.__es = es

    def create_index(self, index_name: str, mapping_filepath: str) -> None:
        logger.debug("create index: {}".format(index_name))

        if not os.path.exists(mapping_filepath):
            logger.error("mapping file not found: {}".format(mapping_filepath))
            sys.exit(errno.ENOENT)

        with open(mapping_filepath) as f:
            mappings = json.load(f)

        try:
            result = self.__es.indices.create(index=index_name, body=mappings)
            logger.debug(result)
        except TransportError as e:
            if e.error == "resource_already_exists_exception":
                # ignore already existing index
                logger.debug(e)
            else:
                raise

    def delete_index(self, index_name: str) -> None:
        logger.debug("delete index: {}".format(index_name))
        self.__es.indices.delete(index=index_name, ignore=404, request_timeout=Default.TIMEOUT)

    def put(self, index_name: str, doc: Dict) -> int:
        logger.debug(doc)

        try:
            self.__es.index(index=index_name, body=doc)
        except RequestError as e:
            logger.error(e)
            return 1

        return 0

    def bulk_put(self, index_name: str, docs: List[Dict]) -> int:
        try:
            r = self.__es.bulk(index=index_name, body=docs)
        except RequestError as e:
            logger.error(e)
            raise RuntimeError(e)

        if r["errors"]:
            r_index = r["items"][0]["index"]

            logger.error(
                "{} {}: {}".format(
                    r_index["status"], r_index["error"]["type"], r_index["error"]["reason"]
                )
            )

            if 400 <= r_index["status"] < 500:
                return 0

            raise RuntimeError()

        logger.debug(json.dumps(docs[:2], indent=4, ensure_ascii=False))

        put_count = len(docs) // 2
        logger.debug("successed to bulk put {} docs".format(put_count))

        return put_count

    def refresh(self, index_name: str) -> None:
        logger.debug("refresh {}".format(index_name))
        self.__es.indices.refresh(index=index_name, request_timeout=Default.TIMEOUT)

    def fetch_stats(self, index_name: str) -> Dict:
        return self.__es.indices.stats(index=index_name, metric="_all")


def create_es_client(host: str, dry_run: bool) -> ElasticsearchClientInterface:
    if dry_run:
        return NullElasticsearchClient()

    try:
        es = Elasticsearch(hosts=[host], sniff_on_start=False)
    except TransportError as e:
        logger.error(e)
        sys.exit(errno.ENETUNREACH)

    return ElasticsearchClient(es)
