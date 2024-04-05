from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from db.User import Base


class Database:
    def __init__(self):
        self.db_path = 'sqlite:///database.db'
        self.engine = create_engine(self.db_path, echo=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_session(self):
        return self.session
