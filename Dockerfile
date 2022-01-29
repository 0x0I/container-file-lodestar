ARG build_version="node:16.13.1-buster-slim"
ARG build_type="source"
ARG lodestar_version=v0.33.0

# ******* Stage: source builder ******* #
FROM ${build_version} as builder-source

ARG lodestar_version

RUN apt update && apt install --yes --no-install-recommends \
  ca-certificates \
  git \
  g++ \
  make \
  python3

WORKDIR /build
RUN git clone --depth 1 --branch ${lodestar_version} https://github.com/ChainSafe/lodestar.git
RUN cd lodestar && yarn install --ignore-optional && yarn run build

RUN ln -s /build/lodestar/lodestar /usr/local/bin/lodestar

# ----- Stage: package install -----
FROM ${build_version} as builder-package

ARG lodestar_version

RUN apt update && apt install --yes --no-install-recommends curl ca-certificates python3 g++ make

WORKDIR /build/lodestar

RUN npm install -g @chainsafe/lodestar-cli

FROM builder-${build_type} as build-condition

# ******* Stage: base ******* #
FROM build-condition as base

RUN apt update && apt install --yes --no-install-recommends \
    ca-certificates \
    cron \
    curl \
    nodejs \
    python3-pip \
    tini \
  # apt cleanup
	&& apt-get autoremove -y; \
	apt-get clean; \
	update-ca-certificates; \
	rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/*

WORKDIR /docker-entrypoint.d
COPY entrypoints /docker-entrypoint.d
COPY scripts/entrypoint.sh /usr/local/bin/lodestar-entrypoint

COPY scripts/lodestar-helper.py /usr/local/bin/lodestar-helper
RUN chmod 775 /usr/local/bin/lodestar-helper

RUN pip3 install click pyaml

ENTRYPOINT ["lodestar-entrypoint"]

# ******* Stage: testing ******* #
FROM base as test

ARG goss_version=v0.3.16

RUN curl -fsSL https://goss.rocks/install | GOSS_VER=${goss_version} GOSS_DST=/usr/local/bin sh

WORKDIR /test

COPY test /test

ENV NODE_OPTIONS=--max-old-space-size=4096
ENV NOLOAD_CONFIG=1

CMD ["goss", "--gossfile", "/test/goss.yaml", "validate"]

# ******* Stage: release ******* #
FROM base as release

ARG version=0.1.0

LABEL 01labs.image.authors="zer0ne.io.x@gmail.com" \
	01labs.image.vendor="O1 Labs" \
	01labs.image.title="0labs/lodestar" \
	01labs.image.description="an open-source Ethereum Consensus (Eth2) client and Typescript ecosystem maintained by ChainSafe Systems" \
	01labs.image.source="https://github.com/0x0I/container-file-lodestar/blob/${version}/Dockerfile" \
	01labs.image.documentation="https://github.com/0x0I/container-file-lodestar/blob/${version}/README.md" \
	01labs.image.version="${version}"

ENV NODE_OPTIONS=--max-old-space-size=4096

WORKDIR /build/lodestar

# beacon-chain node default ports
#
#          discovery/p2p     http api   metrics
#               ↓     ↓        ↓         ↓
EXPOSE    9000/tcp 9000/udp   9596      8008

CMD ["lodestar", "beacon"]
