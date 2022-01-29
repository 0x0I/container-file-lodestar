#!/bin/bash
set -eo pipefail

DIR=/docker-entrypoint.d
if [[ -d "$DIR" ]] ; then
  echo "Executing entrypoint scripts in $DIR"
  /bin/run-parts --exit-on-error "$DIR"
fi

conf="${LODESTAR_CONFIG_DIR:-/etc/lodestar}/config.yml"
if [[ -z "${NOLOAD_CONFIG}" && -f "${conf}" ]]; then
  echo "Loading config at ${conf}..."
  run_args="--rcConfig=${conf} ${EXTRA_ARGS:-}"
else
  run_args=${EXTRA_ARGS:-""}
fi

exec /usr/bin/tini -g -- $@ ${run_args}
