from typing import NamedTuple, Protocol


class Actor(NamedTuple):
    name: str
    url: str


class MoviePagePartial(NamedTuple):
    title: str
    actors: list[Actor]


class MoviePage(NamedTuple):
    url: str
    title: str
    actors: list[Actor]


class FetchProgress(Protocol):
    def on_top_pages_start(self) -> None: ...
    def on_top_pages_done(self, link_count: int) -> None: ...
    def on_movies_start(self, total: int) -> None: ...
    def on_movie_done(self) -> None: ...
    def on_movies_done(self) -> None: ...
