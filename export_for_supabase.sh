#!/bin/bash
# ============================================================
# Export local SQLite data for import into Supabase Postgres.
# Run this BEFORE switching DATABASE_URL in .env to Supabase —
# it must run against the current local database.
#
# Produces supabase_data.json. See the migration steps this
# script prints at the end for what to do with it.
# ============================================================
set -euo pipefail

if [ -d "venv" ] && [ -z "${VIRTUAL_ENV:-}" ]; then
  source venv/bin/activate
fi

if [ -n "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is set in this shell — this script must read the LOCAL"
  echo "SQLite database, not a remote one. Unset it and re-run:"
  echo "  unset DATABASE_URL && bash export_for_supabase.sh"
  exit 1
fi

echo "Exporting local data..."
python manage.py dumpdata \
  --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.permission \
  --exclude admin.logentry --exclude sessions.session \
  --indent 2 -o supabase_data.json

echo ""
echo "Wrote supabase_data.json ($(wc -c < supabase_data.json) bytes)."
echo ""
echo "Next steps:"
echo "  1. In .env, set DATABASE_URL to your Supabase DIRECT connection string"
echo "     (Project Settings -> Database -> Connection string -> URI, port 5432)."
echo "  2. python manage.py migrate"
echo "  3. python manage.py loaddata supabase_data.json"
echo "  4. python manage.py sqlsequencereset products orders payments contact auth | python manage.py dbshell"
echo "     (loaddata writes explicit primary keys; without this the next INSERT"
echo "     collides on an id Postgres thinks is still free.)"
echo "  5. Spot-check row counts, e.g.:"
echo "     python manage.py shell -c \"from products.models import Product; print(Product.objects.count())\""
