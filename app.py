import uuid
from datetime import datetime, timedelta
from typing import TypeVar, Generic

import jwt
import sqlalchemy.exc
from fastapi import FastAPI, Request, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from db.Database import Database
from db.User import User, Category, Author, Books

db_path = 'sqlite:///database.db'

db = Database()
session = db.get_session()

secret_key = 'abc123'

# new_user = User(name='John')
# new_user2 = User(name='Jack')
# session.add(new_user)
# session.add(new_user2)
# users = session.query(User).all()
# print(users[1].name)

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define middleware to check JWT token in header
async def token_checker(request: Request):
    token = request.headers.get('Authorization')
    # print(request.headers.get('Authorization'))
    # raise HTTPException(status_code=401, detail="Token has Expired")
    # return JSONResponse(status_code=401, content={"detail": "Token has expired"})
    if token:
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            request.state.user = payload
            print(payload)
            return None
        except jwt.ExpiredSignatureError:
            # raise HTTPException(status_code=401, detail="Token has expired")
            return JSONResponse(status_code=401, content={"code": 401, "message": "Token has expired"})
        except jwt.InvalidTokenError:
            # raise HTTPException(status_code=401, detail="Invalid token")
            return JSONResponse(status_code=401, content={
                "code": 401,
                "message": "Invalid token"
            })
    else:
        # raise HTTPException(status_code=401, detail="Token not provided")
        return JSONResponse(status_code=401, content={
            "code": 401,
            "message": "Token not provided"
        })


# Register middleware with FastAPI app
# app_protected.middleware('http')(token_checker)
# app.mount("/api", app_public)
# app.mount("/api/auth", app_protected)


@app.get("/api/test")
async def test(token_status: JSONResponse | None = Depends(token_checker)):
    # user = request.state.user
    # print(user.id)
    if token_status:
        return token_status
    return "Hello World2!"


# Define Pydantic model for request schema
class LoginRequest(BaseModel):
    user_name: str
    password: str


class RegisterRequest(BaseModel):
    user_name: str
    email: str
    phone_number: str
    password: str


class CategoryItem(BaseModel):
    category_name: str


class AuthorItem(BaseModel):
    name: str
    description: str


class BookItem(BaseModel):
    name: str
    description: str
    book_cover_url: str
    author_id: str
    category_id: str
    rating: float
    price: float


class AddCategoryRequest(BaseModel):
    categories: list[CategoryItem]


class AddAuthorsRequest(BaseModel):
    authors: list[AuthorItem]


class AddBooksRequest(BaseModel):
    books: list[BookItem]


T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    code: int = Field(default=0, description="Indicates if the request was successful")
    message: str = Field(default=None, description="Message providing additional information")
    data: T | None = Field(default=None, description="Response data")

    def encode(self):
        return jsonable_encoder(self)


class LoginData(BaseModel):
    access_token: str


class LoginResponse(BaseResponse[LoginData]):

    def __init__(self, code: int, message: str, data: LoginData | None):
        super().__init__()
        self.code = code
        self.message = message
        self.data = data


class RegisterResponse(BaseResponse[LoginData]):
    def __init__(self, code: int, message: str, data: LoginData | None):
        super().__init__()
        self.code = code
        self.message = message
        self.data = data


class CategoryDataItem(BaseModel):
    id: str
    category_name: str


class AuthorDataItem(BaseModel):
    id: str
    name: str
    description: str


class BookDataItem(BaseModel):
    id: str
    name: str
    description: str
    book_cover: str
    author: AuthorDataItem
    category: CategoryDataItem
    rating: float
    price: float


class CategoryData(BaseModel):
    categories: list[CategoryDataItem]


class AuthorData(BaseModel):
    authors: list[AuthorDataItem]


class SpecialBooks(BaseModel):
    title: str
    type: str
    books: list[BookDataItem]


class BookData(BaseModel):
    special_books: list[SpecialBooks]
    normal_books: list[BookDataItem]


class SimpleBookData(BaseModel):
    books: list[BookDataItem]


class CategoryListResponse(BaseResponse[CategoryData]):
    def __init__(self, code: int, message: str, data: CategoryData | None):
        super().__init__()
        self.code = code
        self.message = message
        self.data = data


class AuthorListResponse(BaseResponse[AuthorData]):
    def __init__(self, code: int, message: str, data: AuthorData | None):
        super().__init__()
        self.code = code
        self.message = message
        self.data = data


class BookListResponse(BaseResponse[BookData]):
    def __init__(self, code: int, message: str, data: BookData | None):
        super().__init__()
        self.code = code
        self.message = message
        self.data = data


class SimpleBookListResponse(BaseResponse[SimpleBookData]):
    def __init__(self, code: int, message: str, data: SimpleBookData | None):
        super().__init__()
        self.code = code
        self.message = message
        self.data = data


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user: User | None = (session.query(User)
                         .filter(User.name == request.user_name, User.password == request.password).first())
    if user is None:

        return JSONResponse(
            status_code=404,
            content=LoginResponse(code=404, message="User not found", data=None).__dict__)
    else:
        payload = {
            'user_id': user.id.hex,
            'username': user.name,
            'exp': datetime.utcnow() + timedelta(days=1)  # Expiration time (1 day from now)
        }
        # return LoginResponse(data=LoginData(access_token="aa"))


        return  JSONResponse(
            status_code=200,
            content= {
                'code': 0,
                'message': 'Success',
                'data': jwt.encode(payload, algorithm='HS256', key=secret_key)
            }
        )

        # return JSONResponse(
        #     status_code=200,
        #     content=LoginResponse(code=0, message="Success", data=LoginData(
        #         access_token=jwt.encode(payload, algorithm='HS256', key=secret_key))).__dict__)


@app.post("/api/auth/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    user = User(name=request.user_name, email=request.email, password=request.password,
                phone_number=request.phone_number)
    payload = {
        'user_id': user.id,
        'username': user.name,
        'exp': datetime.utcnow() + timedelta(days=1)  # Expiration time (1 day from now)
    }
    token = jwt.encode(payload, algorithm='HS256', key=secret_key)

    try:
        session.add(user)
        session.commit()
        response = RegisterResponse(code=201, message="Success", data=LoginData(access_token=token)).encode()
        return JSONResponse(
            status_code=201,
            content=response,
        )
    except sqlalchemy.exc.IntegrityError as integrity_error:
        print(integrity_error)
        session.rollback()
        return JSONResponse(
            status_code=409,
            content=RegisterResponse(code=409, message="User already exists", data=None).__dict__
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content=RegisterResponse(code=500, message="Something went wrong", data=None).__dict___
        )


@app.post("/api/add_categories")
async def add_categories(request: AddCategoryRequest):
    categories = request.categories
    for category in categories:
        session.add(Category(name=category.category_name))
        session.commit()
    updated_categories: list[CategoryItem] = session.query(Category).all()
    return JSONResponse(status_code=201, content={
        "code": 201,
        "message": "Successfully added",
        "data": {
            "categories": len(updated_categories)
        }
    })


@app.get("/api/user/categories", response_model=CategoryListResponse)
async def get_book_categories(request: Request, token=Depends(token_checker)):
    # if token is not None:
    #     return token
    categories: list[Category] = session.query(Category).all()
    categories_list = list(map(lambda x: CategoryDataItem(id=x.id.hex, category_name=x.name), categories))
    response = CategoryListResponse(code=200, message="Success",
                                    data=CategoryData(categories=categories_list)).encode()
    return JSONResponse(
        status_code=200,
        content=response
    )


@app.post("/api/add_authors")
async def add_categories(request: AddAuthorsRequest):
    authors = request.authors
    for author in authors:
        session.add(
            Author(name=author.name, author_description=author.description)
        )
        session.commit()
    updated_authors: list[AuthorItem] = session.query(Author).all()
    return JSONResponse(status_code=201, content={
        "code": 201,
        "message": "Successfully added",
        "data": {
            "authors": len(updated_authors)
        }
    })


@app.get("/api/user/authors", response_model=AuthorListResponse)
async def get_book_authors(request: Request):
    # if token is not None:
    #     return token
    authors: list[Author] = session.query(Author).all()
    authors_list = list(
        map(lambda x: AuthorDataItem(id=x.id.hex, name=x.name, description=x.author_description), authors))
    response = AuthorListResponse(code=200, message="Success",
                                  data=AuthorData(authors=authors_list)).encode()
    return JSONResponse(
        status_code=200,
        content=response
    )


@app.post("/api/user/add_books")
async def add_books(request: AddBooksRequest):
    books = request.books
    for book in books:
        session.add(
            Books(
                name=book.name,
                book_description=book.description,
                book_cover=book.book_cover_url,
                author_id=book.author_id,
                category_id=book.category_id,
                rating=book.rating,
                price=book.price
            )
        )
        session.commit()
    updated_books: list[BookItem] = session.query(Books).all()
    return JSONResponse(status_code=201, content={
        "code": 201,
        "message": "Successfully added",
        "data": {
            "books": len(updated_books)
        }
    })


@app.get("/api/user/books")
async def get_books(request: Request):
    # if token is not None:
    #     return token
    books: list[Books] = session.query(Books).all()
    print(f"{books[0].author.author_description} books found")

    books_list = list(map(lambda x: BookDataItem(
        id=x.id.hex,
        name=x.name, description=x.book_description, book_cover=x.book_cover,
        author=AuthorDataItem(id=x.author.id.hex, name=x.author.name, description=x.author.author_description),
        category=CategoryDataItem(id=x.category.id.hex, category_name=x.category.name),
        rating=x.rating, price=x.price), books))
    print(f"books list: {books_list}")
    response = BookListResponse(code=200, message="Success",
                                data=BookData(
                                    special_books=[
                                        SpecialBooks(title="Recommended", type="BANNER",
                                                     books=books_list),
                                        SpecialBooks(title="Best Sellers", type="CAROUSEL",
                                                     books=books_list),
                                        SpecialBooks(title="New Arrivals", type="GRID",
                                                     books=books_list),
                                        SpecialBooks(title="Editor Choice", type="CAROUSEL",
                                                     books=books_list)
                                    ],
                                    normal_books=books_list,
                                )).encode()
    return JSONResponse(
        status_code=200,
        content=response
    )


@app.get("/api/user/books_simple")
async def get_books(request: Request):
    # if token is not None:
    #     return token
    books: list[Books] = session.query(Books).all()
    print(f"{books[0].author.author_description} books found")

    books_list = list(map(lambda x: BookDataItem(
        id=x.id.hex,
        name=x.name, description=x.book_description, book_cover=x.book_cover,
        author=AuthorDataItem(id=x.author.id.hex, name=x.author.name, description=x.author.author_description),
        category=CategoryDataItem(id=x.category.id.hex, category_name=x.category.name),
        rating=x.rating, price=x.price), books))
    print(f"books list: {books_list}")
    response = SimpleBookListResponse(code=200, message="Success",
                                      data=SimpleBookData(
                                          books=books_list,
                                      )).encode()
    return JSONResponse(
        status_code=200,
        content=response
    )
