#!/bin/bash
# Run it from the project root directory!!!
# Need reexamine even in context of countries

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Script directory: $SCRIPT_DIR"
echo "Project directory: $PROJECT_DIR"

# delete all generated migration files (keep the folder itself)
rm "$PROJECT_DIR/migrations/versions"/*.py

# delete the database
rm /home/zbyszek/Documents/moje-dokumenty-overt/programowanie-win/databases/SQLite/Quotes/quotes2026.db

source /home/zbyszek/venvs/3_13_4-gui_finance/bin/activate

# change to project directory for alembic commands
cd "$PROJECT_DIR"

# create new initial migration
alembic revision --autogenerate -m "initial"

# apply migration
alembic upgrade head

# seed database
python "$SCRIPT_DIR/seed.py"