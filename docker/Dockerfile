FROM ubuntu:20.04
LABEL maintainer="Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>"

ENV DEBIAN_FRONTEND noninteractive

ARG version
RUN set -eux \
    && apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
    && python3 -m pip install "elasticsearch-faker==${version}" \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["elasticsearch-faker"]
CMD ["--help"]
