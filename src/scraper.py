import asyncio
import itertools
import logging

import httpx

import db
from parser import ParsingError, parse_movie_page, parse_top_page
from services import movie_service
from typedefs import FetchProgress, MoviePage

logger = logging.getLogger(__name__)


async def fetch_with_limiter(async_client: httpx.AsyncClient, url: str, limiter: asyncio.Semaphore) -> httpx.Response:
    async with limiter:
        response = await async_client.get(url)
        response.raise_for_status()
        return response


async def fetch_top_movie_pages(
    async_client: httpx.AsyncClient,
    top_300_urls: list[str],
    *,
    max_connections: int = 4,
) -> list[str]:
    """
    Scrapes data from top movie pages on CSFD.

    Uses scatter/gather asynchronous requests to fetch pages concurrently.
    """
    connection_limiter = asyncio.Semaphore(max_connections)

    results = [fetch_with_limiter(async_client, url, connection_limiter) for url in top_300_urls]
    responses = await asyncio.gather(*results)
    return [response.text for response in responses]


async def fetch_and_parse_movie_page(
    async_client: httpx.AsyncClient,
    link: str,
    connection_limiter: asyncio.Semaphore,
    *,
    csfd_domain: str = "https://www.csfd.cz",
    progress: FetchProgress | None = None,
) -> MoviePage:
    logger.info("Fetching %s", csfd_domain + link)

    response = await fetch_with_limiter(async_client, csfd_domain + link, connection_limiter)

    try:
        movie = parse_movie_page(response.text)
    except ParsingError as exc:
        logger.error("Error parsing movie page %s: %s", csfd_domain + link, exc)
        raise exc

    if progress:
        progress.on_movie_done()

    return MoviePage(url=link, title=movie.title, actors=movie.actors)


async def fetch_movies(
    async_client: httpx.AsyncClient,
    links: list[str],
    *,
    progress: FetchProgress | None = None,
    max_connections: int = 4,
) -> list[MoviePage]:
    """
    Scrapes data from individual movie pages on CSFD.

    Uses scatter/gather asynchronous requests to fetch pages concurrently with a limiter.
    """
    connection_limiter = asyncio.Semaphore(max_connections)

    results = [
        fetch_and_parse_movie_page(
            async_client,
            link,
            progress=progress,
            connection_limiter=connection_limiter,
        )
        for link in links
    ]
    movies = await asyncio.gather(*results)
    return list(movies)


async def scrape_movies_from_urls(
    top_300_urls: list[str],
    max_connections: int,
    *,
    progress: FetchProgress | None = None,
) -> list[MoviePage]:
    async with httpx.AsyncClient() as async_client:
        if progress:
            progress.on_top_pages_start()

        top_300_htmls = await fetch_top_movie_pages(async_client, top_300_urls, max_connections=max_connections)
        link_lists = [parse_top_page(html) for html in top_300_htmls]
        links = list(itertools.chain.from_iterable(link_lists))

        if progress:
            progress.on_top_pages_done(len(links))
            progress.on_movies_start(len(links))

        movies = await fetch_movies(async_client, links, progress=progress, max_connections=max_connections)

        if progress:
            progress.on_movies_done()

        return movies


def scrape_and_save(
    *,
    top_300_urls: list[str],
    db_file: str,
    max_connections: int,
    progress: FetchProgress | None = None,
) -> None:
    """Scrapes data from CSFD and saves it to SQLite database."""
    movies = asyncio.run(scrape_movies_from_urls(top_300_urls, max_connections, progress=progress))

    engine = db.create_disk_engine(db_file)

    # clear existing data
    # this way we don't delete something which is not a database file
    db.Base.metadata.drop_all(engine)
    db.Base.metadata.create_all(engine)

    Session = db.create_session_factory(engine)
    with Session() as session:
        movie_service.save_all(session, movies)
