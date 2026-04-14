# ai_contract.py

"""
AI CONTRACT:

1. SQLAlchemy:
   - Use 2.0 style (select, Session, mapped_column)
   - Never use session.query()

2. Types:
   - Always use Mapped[...] annotations

3. DB:
   - SQLite compatible
   - Avoid DB-specific features

4. Financial data:
   - Use Decimal, not float

5. Relationships:
   - Always explicit with back_populates
"""