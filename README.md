# CSFD Top 300

Scrapes the top 300 movies from [CSFD.cz](https://www.csfd.cz), stores them in SQLite, and serves a search interface.

## Install

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv pip install .
```

## Scraper

Fetches top 300 movies and saves to SQLite:

```bash
uv run scraper
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
```

Open http://localhost:5000. Search movies and actors, click through to detail pages with links back to CSFD.

## Tests

```bash
uv run pytest
```
