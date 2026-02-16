"""
Module for service that can be used both in web and scraper part. Mainly for database access, but also for some shared
logic.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from db import normalize
from models import ActorModel, MovieModel
from typedefs import MoviePage


class MovieService:
    def get_movie(self, session: Session, movie_id: int) -> MovieModel | None:
        return session.execute(select(MovieModel).where(MovieModel.id == movie_id)).scalar_one_or_none()

    def get_actors(self, session: Session, movie_id: int) -> list[ActorModel]:
        movie = session.execute(select(MovieModel).where(MovieModel.id == movie_id)).scalar_one_or_none()
        if not movie:
            return []
        return movie.actors

    def search(self, session: Session, query: str) -> list[MovieModel]:
        q = f"%{normalize(query)}%"
        return list(session.execute(select(MovieModel).where(MovieModel.title_normalized.like(q))).scalars().all())

    def save_all(self, session: Session, movies: list[MoviePage]) -> None:
        for movie in movies:
            movie_record = MovieModel(
                url=movie.url,
                title=movie.title,
                title_normalized=normalize(movie.title),
            )

            for actor in movie.actors:
                actor_record = session.execute(
                    select(ActorModel).where(ActorModel.url == actor.url)
                ).scalar_one_or_none()

                if not actor_record:
                    actor_record = ActorModel(
                        name=actor.name,
                        url=actor.url,
                        name_normalized=normalize(actor.name),
                    )
                movie_record.actors.append(actor_record)

            session.add(movie_record)
            session.flush()
        session.commit()


class ActorService:
    def get_actor(self, session: Session, actor_id: int) -> ActorModel | None:
        return session.execute(select(ActorModel).where(ActorModel.id == actor_id)).scalar_one_or_none()

    def get_movies(self, session: Session, actor_id: int) -> list[MovieModel]:
        actor = session.execute(select(ActorModel).where(ActorModel.id == actor_id)).scalar_one_or_none()
        if not actor:
            return []
        return actor.movies

    def search(self, session: Session, query: str) -> list[ActorModel]:
        q = f"%{normalize(query)}%"
        return list(session.execute(select(ActorModel).where(ActorModel.name_normalized.like(q))).scalars().all())


movie_service = MovieService()
actor_service = ActorService()
