import json
import logging
import pathlib
import random
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.logger import logger
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, BaseLoader
from pydantic import BaseModel

import db

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("server")

GUESS_FILENAME = "guesses/guess_{id_:03d}.json"

TEMPLATE = """
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

  <button id="reload"> Reload </button>
  <button id="random"> Random </button>

  <script src="/static/app.js"></script>
"""

session = db.Session()


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
    def get_random_id() -> int:
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
    def load_guess(id_: int) -> Guess:
        guess_path = pathlib.Path(GUESS_FILENAME.format(id_=id_))
        if guess_path.exists():
            with open(guess_path, "r") as f:
                data = json.load(f)
            logger.info("Data: %s", data)
            guess = Guess(**data)
            logger.info("Loading guess %s", guess)
            return guess
        else:
            logger.info("Guess not found")

    @app.post("/guess_party")
    def guess_party(guess: Guess):
        id_ = guess.id
        logger.info("Writing guess %s", guess)
        with open(GUESS_FILENAME.format(id_=id_), "w") as f:
            json.dump(guess.dict(), f)

    return app


app = init_app(debug=True)
