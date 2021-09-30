from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///db.sqlite", echo=True)
meta = MetaData()
Base = declarative_base(metadata=meta)
Session = sessionmaker(bind=engine)


class Guess(Base):
    __tablename__ = "guesses"

    id = Column(Integer, primary_key=True)
    party = Column(String)
    known = Column(Boolean)

    def __repr__(self):
        return f"Guess(id={self.id}, party={self.party}, known={self.known})"
