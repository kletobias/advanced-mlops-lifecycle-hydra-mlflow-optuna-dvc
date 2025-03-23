## 5. Modular Code Organization

### 5.1 “Dependencies” Folder

This is where you store reusable logic:
- **cleaning**: e.g. `sanitize_column_names.py`
- **io**: read/write CSV or JSON logic
- **metadata**: computing metadata, hashing, etc.
- **modeling**: training logic, logging model importances, etc.

Highlight how each submodule is small and focused, letting you:
- Keep the pipeline scripts lean.
- Avoid rewriting file I/O or logging code repeatedly.
- Achieve easier testing and maintenance.
