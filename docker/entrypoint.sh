#!/bin/bash
set -e
SKIP_MIGRATIONS=${SKIP_MIGRATIONS:=false}
PGP_KEY=${PGP_KEY:=false}
if [ "$SKIP_MIGRATIONS" = false ]; then
  python manage.py wait_for_db
  echo 'running migrations'
  python manage.py migrate
fi
if [ "$PGP_KEY" != false ]; then
  echo "$PGP_KEY" | gpg --import
fi
exec "$@"
