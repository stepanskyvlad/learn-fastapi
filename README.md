# Learn FastAPI

## How to launch server

1. Using uvicorn
```bash
uvicorn books:app --reload
```

2. Using fastapi[standard]
```bash
fastapi dev books.py
```

where the `books` is the name of the main file.

## Pydentic v1 vs Pydentic v2
The three biggest are:

`.dict()` function is now renamed to `.model_dump()`

`schema_extra` function within a Config class is now renamed to `json_schema_extra`

Optional variables need a `=None` example: `id: Optional[int] = None`