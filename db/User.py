import uuid

from sqlalchemy import Column, Integer, String, UUID, Double, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String, unique=True)
    password = Column(String)
    # bookmarks = relationship("book_marks", back_populates="users")
    active_cart_id = Column(Integer, ForeignKey('cart.id'))
    # active_cart = relationship("cart")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)


class Books(Base):
    __tablename__ = 'books'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    book_description = Column(String)
    book_cover = Column(String)
    author_id = Column(String, ForeignKey('authors.id'))
    category_id = Column(String, ForeignKey('categories.id'))
    rating = Column(Double, default=0.0)
    price = Column(Double, default=0.0)

    category = relationship('Category')
    author = relationship("Author")
    # bookmarks = relationship("book_marks", back_populates="books")
    # shoppingcarts = relationship("cart", secondary='book_shoppingcart_association', back_populates="books")


class Author(Base):
    __tablename__ = 'authors'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    author_description = Column(String)


class BookMarks(Base):
    __tablename__ = 'book_marks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey('books.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    # user = relationship("users", back_populates="book_marks")
    # book = relationship("books", back_populates="book_marks")
    is_active = Column(Boolean, default=True)


class Cart(Base):
    __tablename__ = 'cart'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid)
    user_id = Column(UUID(), ForeignKey('users.id'))
    # user = relationship("users", back_populates="active_cart")
    # books = relationship("books", secondary='book_shoppingcart_association', back_populates="cart")
    is_active = Column(Boolean, default=True)


class BookShoppingCartAssociation(Base):
    __tablename__ = 'book_shoppingcart_association'

    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    shoppingcart_id = Column(Integer, ForeignKey('cart.id'), primary_key=True)

    # book = relationship("books", back_populates="cart")
    # shoppingcart = relationship("cart", back_populates="books")
