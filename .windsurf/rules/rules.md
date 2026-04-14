---
trigger: always_on
---
"""
PROJECT RULES FOR AI (Cascade):

- Use SQLAlchemy 2.0 syntax only
- Prefer explicit relationships with back_populates
- Always use Mapped[...] typing
- Avoid implicit joins
- Use Decimal for financial values (never float)
- Follow naming convention from Base.metadata
"""
# Coding Standards
- **Function Length:** No function should exceed 15 lines of code.
- **Refactoring:** If logic is complex, split it into small, descriptive helper functions.
- **Parameters** Always provide types for function parameters
- **Function signatures** Always provide type of returned value if there is any
