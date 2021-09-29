#!/bin/bash
set -e
SKIP_MIGRATIONS=${SKIP_MIGRATIONS:=false}
if [ "$SKIP_MIGRATIONS" = false ]; then
  python manage.py wait_for_db
  echo 'running migations'
  python manage.py migrate
fi
exec "$@"
