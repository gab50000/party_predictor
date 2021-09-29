import pathlib
import random
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, BaseLoader
from pydantic import BaseModel

TEMPLATE = """
<img src="{{img}}">
  <div id="politician_id" value="{{politician_id}}"></div>
  <div>
  {% for party in parties %}
    <input autocomplete="off" type="radio" id="radio-{{party}}" class="party-selector"
     name="party" value="{{party}}" {% if guess == party %} checked {% endif %}>
    <label for="{{party}}">{{party}}</label>
    <br>
  {% endfor %}
  </div>

  <button id="refresh">Refresh </button>

  <script src="/static/app.js"></script>
"""


class Guess(BaseModel):
    id: int
    party: str


TMPL = Environment(loader=BaseLoader()).from_string(TEMPLATE)

app = FastAPI()


app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/")
def root(id_: Optional[int] = None):
    if id_ is None:
        id_ = random.randint(0, 749)

    guess_path = pathlib.Path(f"guess{id_:03d}")
    guess: Optional[str]
    if guess_path.exists():
        guess = guess_path.read_text().strip()
        print("Loading guess", guess)
    else:
        guess = None

    img_name = f"/static/img{id_:03d}.jpg"
    return HTMLResponse(
        TMPL.render(
            img=img_name,
            parties=[
                "AfD",
                "Bündnis 90/Die Grünen",
                "CDU/CSU",
                "Die Linke",
                "FDP",
                "SPD",
                "fraktionslos",
            ],
            politician_id=id_,
            guess=guess,
        )
    )


@app.post("/guess_party")
def guess_party(guess: Guess):
    id_ = guess.id
    party = guess.party
    with open(f"guess{id_:03d}", "w") as f:
        f.write(party)