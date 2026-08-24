#!/bin/bash
set -euo pipefail

gunicorn --bind 0.0.0.0:3000 --workers 1 --timeout 30 dashboard:app &
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 30 api:app
