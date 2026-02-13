from pathlib import Path

import pytest
import respx

from config import Config

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def top_page_html() -> str:
    return (FIXTURES_DIR / "top_page.html").read_text()


@pytest.fixture
def movie_page_html() -> str:
    return (FIXTURES_DIR / "movie_page.html").read_text()


@pytest.fixture
def mocked_httpx(top_page_html: str) -> respx.MockRouter:
    with respx.mock(assert_all_called=False) as respx_mock:
        for url in Config.CSFD_TOP_300_URLS:
            respx_mock.get(url).respond(200, text=top_page_html)
        yield respx_mock
