#!/bin/bash
set -euo pipefail

DIR=/docker-entrypoint.d

if [[ -d "$DIR" ]] ; then
  echo "Executing entrypoint scripts in $DIR"
  /bin/run-parts --exit-on-error "$DIR"
fi

if [[ -n "${LODESTAR_CONFIG_DIR:-""}" ]]; then
  run_args="--rcConfig=${LODESTAR_CONFIG_DIR}/config.toml ${EXTRA_ARGS:-}"
else
  run_args=${EXTRA_ARGS:-""}
fi

if [[ -n "${run_args:-""}" ]]; then
  exec /usr/bin/tini -g -- $@ ${run_args}
else
  exec /usr/bin/tini -g -- "$@"
fi
