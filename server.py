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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("server")


TEMPLATE = """
  <div>
    <input autocomplete="off" type="checkbox" id="radio-known" class="known-selector"
     name="known" value="known">
    <label for="known"> I know that guy! </label>
  </div>

<img id="abgeordneten-img" src="{{img}}">
  <div id="politician_id" value="{{politician_id}}"></div>
  <div>
  {% for party in parties %}
    <input autocomplete="off" type="radio" id="radio-{{party}}" class="party-selector"
     name="party" value="{{party}}" {% if guess == party %} checked {% endif %}>
    <label for="{{party}}">{{party}}</label>
    <br>
  {% endfor %}
  </div>

  <button id="reload"> Reload </button>
  <button id="refresh"> Refresh </button>

  <script src="/static/app.js"></script>
"""


class Guess(BaseModel):
    id: int
    party: str
    known: bool = False


class PolitInfo(BaseModel):
    id: int
    img: str


TMPL = Environment(loader=BaseLoader()).from_string(TEMPLATE)


def init_app(debug):
    app = FastAPI(debug=debug)
    app.mount("/static", StaticFiles(directory="."), name="static")

    @app.get("/")
    def root():
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
            )
        )

    @app.get("/load_info")
    def load_info(id_: Optional[int] = None) -> PolitInfo:
        if id_ is None:
            id_ = random.randint(0, 749)

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
        guess_path = pathlib.Path(f"guesses/guess_{id_:03d}.json")
        if guess_path.exists():
            with open(guess_path, "r") as f:
                data = json.load(f)
            guess = Guess(**data)
            logger.info("Loading guess %s", guess)
            return guess
        else:
            logger.info("Guess not found")

    @app.post("/guess_party")
    def guess_party(guess: Guess):
        id_ = guess.id
        logger.info("Writing guess %s", guess)
        with open(f"guesses/guess{id_:03d}", "w") as f:
            json.dump(guess.json(), f)

    return app


app = init_app(debug=True)
