import pytest

from parser import ParsingError, parse_movie_page, parse_top_page


def test_parse_top_page(top_page_html: str):
    links = parse_top_page(top_page_html)

    assert len(links) == 99
    assert links[0] == "/film/2294-vykoupeni-z-veznice-shawshank/prehled/"
    assert links[1] == "/film/10135-forrest-gump/prehled/"
    assert links[2] == "/film/2292-zelena-mile/prehled/"
    assert links[98] == "/film/22205-princezna-mononoke/prehled/"


def test_parse_movie_page(movie_page_html: str):
    movie = parse_movie_page(movie_page_html)

    assert movie.title == "Vykoupení z věznice Shawshank"
    assert len(movie.actors) == 32
    assert movie.actors[0].name == "Tim Robbins"
    assert movie.actors[0].url == "/tvurce/103-tim-robbins/prehled/"
    assert movie.actors[1].name == "Morgan Freeman"
    assert movie.actors[1].url == "/tvurce/92-morgan-freeman/prehled/"
    assert movie.actors[-1].name == "Ken Magee"
    assert movie.actors[-1].url == "/tvurce/770475-ken-magee/prehled/"


def test_parse_movie_page_missing_title():
    html = "<html><body><div id='creators'><div><h4>Hrají:</h4><a href='/a'>Actor</a></div></div></body></html>"
    with pytest.raises(ParsingError, match="Missing title"):
        parse_movie_page(html)


def test_parse_movie_page_missing_creators_div():
    html = "<html><body><h1>Some Movie</h1></body></html>"
    with pytest.raises(ParsingError, match="Missing creators div"):
        parse_movie_page(html)


def test_parse_movie_page_no_actors():
    html = (
        "<html><body><h1>Silent Animation</h1>"
        "<div id='creators'>"
        "<div><h4>Režie:</h4><a href='/d'>Director</a></div>"
        "<div><h4>Hudba:</h4><a href='/m'>Composer</a></div>"
        "</div></body></html>"
    )
    movie = parse_movie_page(html)

    assert movie.title == "Silent Animation"
    assert movie.actors == []
