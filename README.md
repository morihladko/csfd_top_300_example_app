# CSFD Top 300

Scrapes the top 300 movies from [CSFD.cz](https://www.csfd.cz), stores them in SQLite, and serves a search interface.

## Install

Requires Python 3.14+.

### Using uv

```bash
uv sync
uv pip install .
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Scraper

Fetches top 300 movies and saves to SQLite:

```bash
uv run scraper --help

# or in .venv after pip install
scraper --help
```

Options:

```
--db-file PATH              SQLite database path (default: movies.db)
--max-connections N         Max concurrent connections (default: 4)
```

## Web

Starts the search web interface:

```bash
uv run web

# or in .venv after pip install
web
```

Open http://localhost:5000. Search movies and actors, click through to detail pages with links back to CSFD.

## Tests

```bash
uv run pytest

# or in .venv after pip install .[dev]
pytest
```
