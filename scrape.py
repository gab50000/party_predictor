import pathlib
import time
import requests
from tqdm import trange
from bs4 import BeautifulSoup

from sqlalchemy.dialects.sqlite import insert

import db

URL = (
    "https://www.bundestag.de/ajax/filterlist/de/abgeordnete/862712-862712"
    "?limit={limit}&noFilterSet=true&offset={offset}"
)


def collect_infos(offset=0, limit=20):
    def fix_url(url):
        if url.startswith("/"):
            return f"https://www.bundestag.de{url}"
        return url

    url = URL.format(offset=offset, limit=limit)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="lxml")
    imgs = soup.find_all("img")
    a_tags = soup.find_all("a", attrs={"title": True})
    ps = soup.find_all("p", attrs={"class": "bt-person-fraktion"})
    infos = []
    for img, p, a in zip(imgs, ps, a_tags):
        info = {
            "name": a["title"],
            "url": fix_url(img["data-img-md-normal"]),
            "partei": p.text.strip(),
        }
        infos.append(info)
    return infos


def scrape_all():
    abgeordnete = []
    for offset in trange(0, 800, 20):
        abgeordnete.extend(collect_infos(offset))
    return abgeordnete


def get_ext(url):
    *_, ext = url.rpartition(".")
    return ext


def download_image(url) -> bytes:
    print("Download", url)
    try:
        r = requests.get(url)
    except:
        breakpoint()

    return r.content


def scrape():
    infos = scrape_all()

    for id_, info in enumerate(infos):
        img_data = download_image(info["url"])
        member = db.BundestagMember(id=id_, name=info["name"], party=info["partei"])
        member_img = db.MemberPhoto(
            id=id_, image=img_data, image_format=info["url"].split(".")[-1]
        )
        session = db.Session()
        try:
            session.merge(member)
            session.merge(member_img)
            session.commit()
        except:
            session.rollback()
        finally:
            session.commit()


if __name__ == "__main__":
    scrape()