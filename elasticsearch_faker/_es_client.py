import abc
import errno
import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (
    AuthenticationException,
    BadRequestError,
    ConnectionError,
    NotFoundError,
    RequestError,
    TransportError,
)

from ._const import Default
from ._logger import logger


class ElasticsearchClientInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create_index(self, index_name: str, mapping_filepath: str) -> int:
        return 0

    @abc.abstractmethod
    def delete_index(self, index_name: str) -> None:
        pass

    @abc.abstractmethod
    def put(self, index_name: str, doc: Dict) -> int:
        pass

    @abc.abstractmethod
    def bulk_put(self, index_name: str, docs: List[Dict]) -> int:
        pass

    @abc.abstractmethod
    def refresh(self, index_name: str) -> None:
        pass

    @abc.abstractmethod
    def count_docs(self, index_name: str) -> int:
        pass

    @abc.abstractmethod
    def fetch_stats(self, index_name: str) -> Dict:
        pass


class NullElasticsearchClient(ElasticsearchClientInterface):
    def create_index(self, index_name: str, mapping_filepath: str) -> int:
        logger.debug(f"create index: {index_name}")
        return 0

    def delete_index(self, index_name: str) -> None:
        logger.debug(f"delete index: {index_name}")

    def put(self, index_name: str, doc: Dict) -> int:
        logger.debug(f"put a doc to {index_name}")
        print(json.dumps(doc, indent=4))
        return 0

    def bulk_put(self, index_name: str, docs: List[Dict]) -> int:
        num_docs = len(docs) // 2
        logger.debug(f"put {num_docs} docs to {index_name}")
        print(json.dumps(docs, indent=4))
        return num_docs

    def refresh(self, index_name: str) -> None:
        logger.debug(f"refresh {index_name}")

    def count_docs(self, index_name: str) -> int:
        return 0

    def fetch_stats(self, index_name: str) -> Dict:
        return {"primaries": {"store": {"size_in_bytes": 0}}}


class ElasticsearchClient(ElasticsearchClientInterface):
    def __init__(self, es: Elasticsearch) -> None:
        self.__es = es

    def create_index(self, index_name: str, mapping_filepath: str) -> int:
        logger.debug(f"create index: {index_name}")

        mappings = {}
        if mapping_filepath:
            if not os.path.exists(mapping_filepath):
                logger.error(f"mapping file not found: {mapping_filepath}")
                return errno.ENOENT

            with open(mapping_filepath) as f:
                mappings = json.load(f)

        try:
            result = self.__es.indices.create(index=index_name, body=mappings)
            logger.debug(result)
        except AuthenticationException as e:
            logger.error(e)
            return errno.EACCES
        except ConnectionError as e:
            logger.error(e)
            return errno.ECOMM
        except BadRequestError as e:
            if e.error == "resource_already_exists_exception":
                logger.debug(f"skip existing index creation: {e}")
            else:
                raise

        return 0

    def delete_index(self, index_name: str) -> None:
        logger.debug(f"delete index: {index_name}")
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
            r = self.__es.bulk(index=index_name, body=docs, timeout="180s")
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
        logger.debug(f"successed to bulk put {put_count} docs")

        return put_count

    def flush(self, index_name: str) -> None:
        logger.debug(f"flush {index_name}")
        self.__es.indices.flush(index=index_name, request_timeout=Default.TIMEOUT)

    def refresh(self, index_name: str) -> None:
        logger.debug(f"refresh {index_name}")
        self.__es.indices.refresh(index=index_name, request_timeout=Default.TIMEOUT)

    def count_docs(self, index_name: str) -> int:
        resp = self.__es.cat.count(index=index_name, params={"h": "count"})
        return int(str(resp))

    def fetch_stats(self, index_name: str) -> Dict:
        try:
            stats = self.__es.indices.stats(index=index_name, metric="_all")
        except AuthenticationException as e:
            logger.error(e)
            sys.exit(errno.EPERM)
        except NotFoundError as e:
            logger.error(e)
            sys.exit(errno.ENOENT)

        return stats["indices"][index_name]


@dataclass
class ElasticsearchClientParameter:
    endpoint: str
    verify_certs: bool = False
    basic_auth_user: Optional[str] = None
    basic_auth_password: Optional[str] = None
    ssl_assert_fingerprint: Optional[str] = None

    @property
    def basic_auth(self) -> Optional[Tuple[str, str]]:
        if self.basic_auth_user is None or self.basic_auth_password is None:
            return None

        return (self.basic_auth_user, self.basic_auth_password)


def create_es_client(
    es_client_param: ElasticsearchClientParameter, dry_run: bool
) -> ElasticsearchClientInterface:
    if dry_run:
        return NullElasticsearchClient()

    try:
        es = Elasticsearch(
            hosts=[es_client_param.endpoint],
            sniff_on_start=False,
            verify_certs=es_client_param.verify_certs,
            basic_auth=es_client_param.basic_auth,
            ssl_assert_fingerprint=es_client_param.ssl_assert_fingerprint,
        )
    except TransportError as e:
        logger.error(e)
        sys.exit(errno.ENETUNREACH)

    return ElasticsearchClient(es)
