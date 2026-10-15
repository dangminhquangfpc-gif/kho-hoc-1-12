#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
name="khohoc-rls-${RANDOM}-${RANDOM}"
# Isolated disposable DB; trust auth is limited to the container, no published ports.
docker run -d --name "$name" -e POSTGRES_HOST_AUTH_METHOD=trust postgres:17 >/dev/null
trap 'docker rm -f "$name" >/dev/null' EXIT
for n in {1..30}; do
  if docker exec "$name" pg_isready -U postgres >/dev/null 2>&1; then break; fi
  sleep 1
done
docker exec "$name" pg_isready -U postgres >/dev/null
for file in supabase/tests/bootstrap_local.sql supabase/migrations/202610140001_mvp.sql supabase/migrations/202610140001_mvp.sql supabase/migrations/202610140002_catalog.sql supabase/tests/rls.sql; do
  docker exec -i "$name" psql -U postgres -v ON_ERROR_STOP=1 < "$file"
done
