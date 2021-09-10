import asyncio
import pathlib
import time
from functools import lru_cache
import requests
from tqdm import trange
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession, HTMLSession


URL = "https://www.bundestag.de/ajax/filterlist/de/abgeordnete/525246-525246?limit={limit}&noFilterSet=true&offset={offset}"


def collect_infos(offset=0, limit=20):
    def fix_url(url):
        if url.startswith("/"):
            return f"https://www.bundestag.de{url}"
        return url

    url = URL.format(offset=offset, limit=limit)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="lxml")
    imgs = soup.find_all("img")
    ps = soup.find_all("p", attrs={"class": "bt-person-fraktion"})
    img_urls = [
        {
            "name": img["alt"],
            "url": fix_url(img["data-img-md-normal"]),
            "partei": p.text.strip(),
        }
        for img, p in zip(imgs, ps)
    ]
    return img_urls


def scrape_all():
    abgeordnete = []
    for offset in trange(0, 800, 20):
        abgeordnete.extend(collect_infos(offset))
    return abgeordnete


class Scraper:
    open_connections = 0
    limit = 3

    @classmethod
    def download_image(cls, session, url, filename):
        print("Open connections:", cls.open_connections)
        # while cls.open_connections >= cls.limit:
        #     print("Sleeping..")
        #     await asyncio.sleep(1)
        cls.open_connections += 1

        print("Download", url)
        try:
            r = session.get(url)
        except:
            breakpoint()
        *_, ext = url.rpartition(".")
        with open(f"{filename}.{ext}", "wb") as f:
            f.write(r.content)
        cls.open_connections -= 1


def write_info(info, filename):
    with open(filename, "w") as f:
        print("Name:", info["name"], file=f)
        print("Partei:", info["partei"], file=f)


def scrape():
    infos = scrape_all()
    session = HTMLSession()

    for i, info in enumerate(infos):
        info_filename = f"info{i:03d}"
        img_filename = f"img{i:03d}"
        if not (
            pathlib.Path(info_filename).exists() or pathlib.Path(img_filename).exists()
        ):
            Scraper.download_image(session, info["url"], img_filename)
            time.sleep(0.1)
            write_info(info, info_filename)
