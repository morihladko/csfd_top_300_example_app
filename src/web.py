from flask import Flask, abort, render_template, request

import db
from config import Config
from services import actor_service, movie_service

app = Flask(__name__)
app.config.from_object(Config)


engine = db.create_memory_engine()
Session = db.create_scope_session(engine)

with app.app_context():
    db.load_from_disk(Config.DB_FILE, engine)


@app.teardown_appcontext
def remove_session(exception=None) -> None:
    Session.remove()


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/search_movies")
def search_movies_route() -> str:
    q = request.args.get("q", "")

    if not q:
        return render_template("_movies.html", movies=[])

    with Session() as session:
        movies = movie_service.search(session, q)

    return render_template("_movies.html", movies=movies)


@app.route("/search_actors")
def search_actors_route() -> str:
    q = request.args.get("q", "")
    if not q:
        return render_template("_actors.html", actors=[])

    with Session() as session:
        actors = actor_service.search(session, q)

    return render_template("_actors.html", actors=actors)


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id: int) -> str:
    with Session() as session:
        movie = movie_service.get_movie(session, movie_id)

        if not movie:
            abort(404)

        actors = movie_service.get_actors(session, movie_id)

    return render_template("movie.html", movie=movie, actors=actors)


@app.route("/actor/<int:actor_id>")
def actor_detail(actor_id: int) -> str:
    with Session() as session:
        actor = actor_service.get_actor(session, actor_id)

        if not actor:
            abort(404)

        movies = actor_service.get_movies(session, actor_id)

    return render_template("actor.html", actor=actor, movies=movies)


def run() -> None:
    app.run()


if __name__ == "__main__":
    run()
