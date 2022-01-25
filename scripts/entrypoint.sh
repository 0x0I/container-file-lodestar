#!/bin/bash
set -euo pipefail

DIR=/docker-entrypoint.d

if [[ -d "$DIR" ]] ; then
  echo "Executing entrypoint scripts in $DIR"
  /bin/run-parts --exit-on-error "$DIR"
fi

if [[ -n "${EXTRA_ARGS:-""}" ]]; then
  exec /usr/bin/tini -g -- $@ ${EXTRA_ARGS}
else
  exec /usr/bin/tini -g -- "$@"
fi
