"""
seed.py — Populate the database with initial reference data.

Run with:  python seed.py

This script is IDEMPOTENT — safe to run multiple times.
It will only insert rows that don't already exist.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from zb_quotes.models.models import Fit

# ── Database connection ───────────────────────────────────────────────────────
DATABASE_URL = "sqlite:////home/zbyszek/Documents/moje-dokumenty-overt/programowanie-win/databases/SQLite/Quotes/quotes2026.db"
engine = create_engine(DATABASE_URL, echo=False)


# ── Seed data definitions ─────────────────────────────────────────────────────

FIT_DATA = [
    {"id": 1, "name": "Cash",      "description": "Physical or digital cash"},
    {"id": 2, "name": "Shares",    "description": "Equity shares / stocks"},
    {"id": 3, "name": "Bonds",     "description": "Fixed income instruments"},
    {"id": 4, "name": "Deposit",   "description": "Bank deposits"},
    {"id": 5, "name": "Forex",     "description": "Foreign exchange instruments"},
    {"id": 6, "name": "Commodity", "description": "Raw materials and commodities"},
]


# ── Helper: upsert-style insert ───────────────────────────────────────────────

def seed_table(session: Session, model, data: list[dict], label: str):
    """
    Insert rows that don't already exist (matched by primary key 'id').
    Prints a summary of what was inserted vs. skipped.
    """
    inserted = 0
    skipped  = 0

    for row in data:
        existing = session.get(model, row["id"])
        if existing is None:
            session.add(model(**row))
            inserted += 1
        else:
            skipped += 1

    print(f"  {label:<20} inserted: {inserted:>3}   skipped (already exist): {skipped:>3}")


# ── Main seed function ────────────────────────────────────────────────────────

def run_seed():
    print("\n=== Seeding database ===\n")

    with Session(engine) as session:
        seed_table(session, Fit, FIT_DATA, "Financial Inst. Types")

        session.commit()

    print("\n=== Done ===\n")


if __name__ == "__main__":
    run_seed()