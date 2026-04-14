---
trigger: always_on
---

# Python Import Conventions

## Datetime Import Rule
- NEVER use `from datetime import datetime`
- ALWAYS use `import datetime as dt`
- When you need the datetime class, access it as `dt.datetime`

## Example of CORRECT import:
```python
import datetime as dt
```

# Then use dt.datetime
now = dt.datetime.now()

## Import from the same project Rule
- NEVER use relative import
- ALWAYS use `from zb_quotes' followed by the path and module name
