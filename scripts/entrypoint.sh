#!/bin/bash
set -euo pipefail

DIR=/docker-entrypoint.d

if [[ -d "$DIR" ]] ; then
  echo "Executing entrypoint scripts in $DIR"
  /bin/run-parts --exit-on-error "$DIR"
fi

conf="${LODESTAR_CONFIG_DIR:-/etc/lodestar}/config.yml"
if [[ -z "${DISABLE_RUNARGS+x}" && -f "${conf}" ]]; then
    run_args="--rcConfig=${conf} ${EXTRA_ARGS:-}"
elif [[ -z "${DISABLE_RUNARGS+x}" ]]; then
    run_args="${EXTRA_ARGS:-}"
fi

exec /usr/bin/tini -g -- $@ ${run_args:-}
