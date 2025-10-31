#!/bin/bash
set -e
MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
RUN_MIGRATIONS=${RUN_MIGRATIONS:=true}
PULL_IDP_METADATA=${PULL_IDP_METADATA:=false}
TEST=${TEST:=false}
PGP_KEY=${PGP_KEY:=false}
python manage.py wait_for_db
python manage.py createcachetable

if [ "${PULL_IDP_METADATA,,}" = true ]; then
  echo "Pulling idp metadata"
  python manage.py update_mitid_idp_metadata
fi
if [ "${MAKE_MIGRATIONS,,}" = true ]; then
  echo 'generating migrations'
  python manage.py makemigrations
fi
if [ "${RUN_MIGRATIONS,,}" = true ]; then
  echo 'running migrations'
  python manage.py migrate
fi
if [ "${TEST,,}" = true ]; then
  echo 'running tests!'
  python manage.py test
fi
if [ "${PGP_KEY,,}" != false ]; then
  echo "$PGP_KEY" | gpg --import
fi
exec "$@"
