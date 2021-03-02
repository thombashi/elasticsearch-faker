#!/usr/bin/env python3

import multiprocessing

from elasticsearch_faker.__main__ import cmd


if __name__ == "__main__":
    multiprocessing.freeze_support()
    cmd()
