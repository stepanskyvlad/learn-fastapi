"""
Don't rely on the trailing slash to distinguish logic. FastAPI treats `/path` and `/path/` as
the same route.

The one hard rule is that any path with a literal segment (e.g. /books/count) or
a more specific pattern (/books/by_author/{author}) must be declared before your
generic dynamic path (/books/{book_title}), otherwise “count” or “by_author” gets
captured as book_title="count" or "by_author".

Follow that same pattern whenever you add new routes:
1. Collection root (/resource/)
2. Statics (fixed paths)
3. Specific dynamics (e.g. /resource/by_xxx/{val})
4. Generic dynamics (/resource/{id})
5. Mutations (POST/PUT/DELETE)

Best practice: when to use static vs query vs dynamic
1. Static paths
Use them for fixed, orthogonal actions or sub-resources that aren't “one-of-a-collection.”

Examples:
* /books/count
* /books/stats/top

2. Dynamic parameters (/{param})
Use them to identify a single resource or to express a clear hierarchy:
* Single item: /books/{book_id}
* Nested resource: /authors/{author}/books or /books/{book_id}/reviews

3. Query parameters
Use them for optional filters, sorting, paging, and other modifiers on a collection endpoint.
Examples:
GET /books/?category=math&author=Jane%20Doe&page=2&limit=10
"""

from fastapi import FastAPI, Body, Query

app = FastAPI()

BOOKS: list[dict[str, str]] = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"},
]


# First simple example
# @app.get("/books")
# async def read_all_books() -> list[dict[str, str]]:
#     return BOOKS


# -------------The correct order of endpoints------------------


# 1. LIST (with optional "category" filter)
# Query parameter - "category"
@app.get("/books/", response_model=list[dict[str, str]])
async def get_all_book(category: str | None = Query(None)):
    if category:
        books_with_category: list[dict[str, str]] = []
        for book in BOOKS:
            if book.get("category").casefold() == category.casefold():
                books_with_category.append(book)
        return books_with_category

    return BOOKS


# 2. SPECIFIC STATIC (specific static "count" after root "books")
# No parameters
@app.get("/books/count")
async def count_books():
    return {"count": len(BOOKS)}


# 3. SPECIFIC DYNAMIC (after specific static "by_author" comes dynamic "author")
# Dynamic parameter - "author"
@app.get("/books/by_author/{author}")
async def get_books_by_author(author: str):
    books_by_author: list[dict[str, str]] = []
    for book in BOOKS:
        if book.get("author").casefold() == author.casefold():
            books_by_author.append(book)
    return books_by_author    


# 4. GENERIC DYNAMIC (dynamic after root "books")
# Dynamic parameter - "title"
@app.get("/books/{book_title}")
async def get_books_by_title(book_title: str):
    for book in BOOKS:
        if book.get("title").casefold() == book_title.casefold():
            return book
        

# Path dynamic and query parameters example
# Change root to "author" to not have a conflict with "/book/{book_title}"
@app.get("/author/{author}/")
async def read_author_category_by_query(
    author: str, category: str
) -> list[dict[str, str]]:
    books_to_return: list[dict[str, str]] = []
    for book in BOOKS:
        if (
            book.get("author").casefold() == author.casefold()
            and book.get("category").casefold() == category.casefold()
        ):
            books_to_return.append(book)
    return books_to_return


# 5. Mutations (POST/PUT/DELETE)
@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)


@app.put("/books/update_book")
async def update_book(updated_book: dict[str, str] = Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == updated_book.get("title").casefold():
            BOOKS[i] = updated_book


@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == book_title.casefold():
            BOOKS.pop(i)
            break
