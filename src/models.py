from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base

movie_actors = Table(
    "movie_actors",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("actor_id", Integer, ForeignKey("actors.id"), primary_key=True),
)


class MovieModel(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str]
    title_normalized: Mapped[str] = mapped_column(index=True, comment="Normalized title for search")

    actors: Mapped[list["ActorModel"]] = relationship(secondary=movie_actors, back_populates="movies")


class ActorModel(Base):
    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    url: Mapped[str] = mapped_column(unique=True)
    name_normalized: Mapped[str] = mapped_column(index=True, comment="Normalized name for search")

    movies: Mapped[list["MovieModel"]] = relationship(secondary=movie_actors, back_populates="actors")
