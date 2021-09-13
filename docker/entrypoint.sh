#!/bin/bash
set -e
python manage.py wait_for_db
echo 'running migations'
python manage.py migrate
exec "$@"
