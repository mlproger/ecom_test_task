#!/usr/bin/env sh
set -euo pipefail

# ожидание БД, миграции и т.п.
until psql "$DATABASE_URL" -c 'SELECT 1' >/dev/null 2>&1; do
  echo 'Waiting for DB...'
  sleep 1
done
psql "$DATABASE_URL" -f /app/migrations/create_tables.sql
# Запустить команду из CMD, заменив shell текущим процессом
exec "$@"