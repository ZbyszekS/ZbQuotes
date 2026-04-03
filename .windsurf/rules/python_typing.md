# Type Hinting for Optional Attributes

When an instance attribute can legitimately be `None` (especially before initialization or after cleanup), always use:

- `Type | None` (preferred in Python 3.10+)

do not use:
- `Optional[Type]` 

Always use types for parameters of the functions and methods.