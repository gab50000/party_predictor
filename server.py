import logging
import pathlib
import random
from typing import Optional

from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, BaseLoader
from pydantic import BaseModel
from sqlalchemy import select

import db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("server")

GUESS_FILENAME = "guesses/guess_{id_:03d}.json"

TEMPLATE = """
  <div>
    <input autocomplete="off" type="checkbox" id="radio-show-only-unlabeled" 
     name="toggle-unlabeleld" value="toggle-known">
    <label for="toggle-unlabeled"> Show only unlabeled politicians </label>
  </div>

  <div>
    <input autocomplete="off" type="checkbox" id="radio-known" class="known-selector"
     name="known" value="known" {% if known %} checked {% endif %} >
    <label for="known"> I know that guy! </label>
  </div>

<img id="abgeordneten-img" src="{{img}}">
  <div id="politician_id" value="{{id}}"></div>
  <div>
  {% for party in parties %}
    <input autocomplete="off" type="radio" id="radio-{{party}}" class="party-selector"
     name="party" value="{{party}}" {% if guess == party %} checked {% endif %}>
    <label for="{{party}}">{{party}}</label>
    <br>
  {% endfor %}
  </div>

  <button id="random"> Random </button>

  <script src="/static/app.js"></script>
"""


class Guess(BaseModel):
    id: int
    party: Optional[str]
    known: bool = False


class PolitInfo(BaseModel):
    id: int
    img: str


TMPL = Environment(loader=BaseLoader()).from_string(TEMPLATE)


def init_app(debug):
    app = FastAPI(debug=debug)
    app.mount("/static", StaticFiles(directory="."), name="static")

    @app.get("/")
    def root(id_: Optional[int] = None):
        if id_ is None:
            return HTMLResponse(
                """
            <head>
                <meta http-equiv="Refresh" content="0; URL=/?id_=0">
            </head>"""
            )

        return HTMLResponse(
            TMPL.render(
                parties=[
                    "AfD",
                    "Bündnis 90/Die Grünen",
                    "CDU/CSU",
                    "Die Linke",
                    "FDP",
                    "SPD",
                    "fraktionslos",
                ],
                id=id_,
                img=f"/static/{load_info(id_).img}",
            )
        )

    @app.get("/random_id")
    def get_random_id(load_only_unknown: bool = False) -> int:
        if load_only_unknown:
            session = db.Session()
            query = select(db.Guess.id)
            result = session.execute(query).all()
            if result:
                labeled_ids = [id_[0] for id_ in result]
                unlabeled_ids = [i for i in range(0, 750) if i not in labeled_ids]
                return random.choice(unlabeled_ids)
            return 0

        return random.randint(0, 749)

    @app.get("/load_info")
    def load_info(id_: int) -> PolitInfo:
        for ext in ("jpg", "png"):
            img = f"img{id_:03d}.{ext}"
            img_path = pathlib.Path(img)
            if img_path.exists():
                break
        else:
            raise Exception("No image found!")

        info = PolitInfo(id=id_, img=img)
        logger.info("Loading info %s", info)
        return info

    @app.get("/load_guess")
    def load_guess(id_: int) -> Optional[Guess]:
        session = db.Session()
        result = session.query(db.Guess).filter(db.Guess.id == id_).first()

        guess: Optional[Guess]
        if result is not None:
            logger.info("Found guess %s in db", result)
            data = {"id": result.id, "party": result.party, "known": result.known}
            guess = Guess(**data)
        else:
            logger.info("Guess not found")
            guess = None
        return guess

    @app.post("/guess_party")
    def guess_party(guess: Guess):
        session = db.Session()
        id_ = guess.id
        entry = session.query(db.Guess).filter(db.Guess.id == id_).first()

        if entry:
            logger.info("Update guess %s", guess)
            entry.id = guess.id
            entry.party = guess.party
            entry.known = guess.known
        else:
            logger.info("Create new guess %s", guess)
            session.add(db.Guess(**guess.__dict__))

        session.commit()

    return app


app = init_app(debug=True)
