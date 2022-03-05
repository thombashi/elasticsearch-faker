FROM ubuntu:20.04
LABEL maintainer="Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>"

ENV DEBIAN_FRONTEND noninteractive

ARG version
ARG extras

RUN set -eux \
    && apt-get -qq update \
    && apt-get install -qq --no-install-recommends \
    python3 \
    python3-pip \
    && python3 -m pip install --retries 30 "elasticsearch-faker[${extras}]==${version}" --disable-pip-version-check \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["elasticsearch-faker"]
CMD ["--help"]
