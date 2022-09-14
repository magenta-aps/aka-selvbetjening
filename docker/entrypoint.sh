#!/bin/bash
set -e
SKIP_MIGRATIONS=${SKIP_MIGRATIONS:=false}
SKIP_IDP_METADATA=${SKIP_IDP_METADATA:=false}
TEST=${TEST:=false}
PGP_KEY=${PGP_KEY:=false}
python manage.py compilemessages
python manage.py wait_for_db
python manage.py createcachetable
if [ "$SKIP_IDP_METADATA" = false ]; then
  python manage.py update_mitid_idp_metadata
fi
if [ "$SKIP_MIGRATIONS" = false ]; then
  echo 'running migrations'
  python manage.py migrate
fi
if [ "$TEST" = true ]; then
  echo 'running tests!'
  python manage.py test
fi
if [ "$PGP_KEY" != false ]; then
  echo "$PGP_KEY" | gpg --import
fi
exec "$@"
