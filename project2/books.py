from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status


app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_year: int


    def __init__(self, id: int, title: str, author: str, description: str, rating: int, published_year: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_year = published_year


class BookRequest(BaseModel):
    id: int | None = Field(description="ID is not needed on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(ge=1, le=5)
    published_year: int = Field(ge=1000, le=2100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "Author 1",
                "description": "A description for a book",
                "rating": 5,
                "published_year": 2025
            }
        }
    }


def find_book_id(book: Book):
    if len(BOOKS) > 0:
        book.id = BOOKS[-1].id + 1
    else: 
        book.id = 1

    return book


BOOKS: list[Book] = [
    Book(1, "Book1", "Author1", "Description1", 5, 2001),
    Book(2, "Book2", "Author2", "Description2", 4, 2001),
    Book(3, "Book3", "Author3", "Description3", 3, 2002),
    Book(4, "Book4", "Author4", "Description4", 5, 2002),
    Book(5, "Book5", "Author5", "Description5", 2, 2001),
    Book(6, "Book6", "Author6", "Description6", 1, 2002),
]


@app.get("/books/all_books", status_code=status.HTTP_200_OK)
async def get_all_books():
    """
    When you return a Python object (or a list of them), 
    FastAPI uses its JSONableEncoder to turn it into JSON.

    For plain classes, it takes their .__dict__ (attribute dict) 
    and makes JSON objects (i.e. Python dicts) out of them.

    Result: your browser or client sees a JSON array of objects 
    (each object is a dict of id, title, etc.), not literal Book(...) instances.
    """
    return BOOKS


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(ge=0, le=5)):
    books_with_target_rating: list[Book] = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_with_target_rating.append(book)
    return books_with_target_rating


@app.get("/books/year_filer/", status_code=status.HTTP_200_OK)
async def read_book_by_published_year(published_year: int = Query(ge=1000, le=2100)):
    books_with_target_publish_year: list[Book] = []
    for book in BOOKS:
        if book.published_year == published_year:
            books_with_target_publish_year.append(book)
    return books_with_target_publish_year


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Item not found")


@app.post("/create_book/", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    # book_request.model_dump() returns a Python dict:
    # {
    #     "id": None,
    #     "title": "My New Title",
    #     "author": "Me",
    #     "description": "…",
    #     "rating": 4
    # }
    # Book(**that_dict)
    # 
    # The ** operator unpacks the dict into keyword arguments.
    # It's equivalent to:
    # Book(
    #     id=that_dict["id"],
    #     title=that_dict["title"],
    #     author=that_dict["author"],
    #     description=that_dict["description"],
    #     rating=that_dict["rating"],
    # )
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))


@app.put("/books/update_book/", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest):
    is_book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i] = Book(**book_request.model_dump())
            is_book_changed = True
            break
    if not is_book_changed:
        raise HTTPException(status_code=404, detail="Item not found.")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    is_book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            is_book_changed = True
            break
    if not is_book_changed:
        raise HTTPException(status_code=404, detail="Item not found.")