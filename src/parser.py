import logging

from bs4 import BeautifulSoup

from typedefs import Actor, MoviePagePartial

logger = logging.getLogger(__name__)


class ParsingError(Exception):
    pass


def parse_top_page(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    movie_links = soup.select("div.tab-content a.film-title-name")

    return [str(link["href"]) for link in movie_links]


def parse_movie_page(html: str) -> MoviePagePartial:
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.select_one("h1")
    if not title_el:
        raise ParsingError("Missing title element in movie page")
    title = title_el.get_text(strip=True)

    actors: list[Actor] = []
    creators_divs = soup.select("#creators")

    if len(creators_divs) == 0:
        raise ParsingError("Missing creators div in movie page")

    if len(creators_divs) > 1:
        raise ParsingError("Multiple creators divs in movie page")

    creators_div = creators_divs[0]
    for div in creators_div.find_all("div", recursive=False):
        h4 = div.find("h4")
        if h4 and "Hrají:" in h4.get_text():
            for a in div.select("a:not(.more)"):
                href = a.get("href")
                name = a.get_text(strip=True)
                if href and name:
                    actors.append(Actor(name=name, url=str(href)))
            break

    return MoviePagePartial(title=title, actors=actors)
