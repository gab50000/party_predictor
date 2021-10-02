import pathlib
import time
import requests
from tqdm import trange
from bs4 import BeautifulSoup


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


def get_ext(url):
    *_, ext = url.rpartition(".")
    return ext


def download_image(session, url, filename):
    print("Download", url)
    try:
        r = session.get(url)
    except:
        breakpoint()
    with open(filename, "wb") as f:
        f.write(r.content)


def write_info(info, filename):
    with open(filename, "w") as f:
        print("Name:", info["name"], file=f)
        print("Partei:", info["partei"], file=f)


def scrape():
    infos = scrape_all()
    session = requests.Session()

    for i, info in enumerate(infos):
        info_filename = f"info{i:03d}"
        img_filename = f"img{i:03d}.{get_ext(info['url'])}"
        if not (
            pathlib.Path(info_filename).exists() and pathlib.Path(img_filename).exists()
        ):
            download_image(session, info["url"], img_filename)
            time.sleep(0.1)
            write_info(info, info_filename)


if __name__ == "__main__":
    scrape()