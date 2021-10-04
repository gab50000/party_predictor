from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    LargeBinary,
    MetaData,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

engine = create_engine("sqlite:///db.sqlite", echo=True)
meta = MetaData()
Base = declarative_base(metadata=meta)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class Guess(Base):
    __tablename__ = "guesses"

    id = Column(Integer, primary_key=True)
    party = Column(String)
    known = Column(Boolean)

    def __repr__(self):
        return f"Guess(id={self.id}, party={self.party}, known={self.known})"


class BundestagMember(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    party = Column(String)


class MemberPhoto(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, unique=True)
    image = Column(LargeBinary)
    image_format = Column(String)


meta.create_all(engine)
