"""
Scraper CLI interface. Provides command-line interface for running the scraper using the `click` library, and uses
`rich` for displaying progress bars and other output in the terminal.
"""

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn

from config import Config
from scraper import scrape_and_save

console = Console()


class RichFetchProgress:
    def __init__(self) -> None:
        self._progress: Progress | None = None
        self._task_id = None

    def on_top_pages_start(self) -> None:
        console.print("  Fetching top pages...")

    def on_top_pages_done(self, link_count: int) -> None:
        console.print(f"[green]✓[/green] Fetched top pages ({link_count} links)")

    def on_movies_start(self, total: int) -> None:
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeRemainingColumn(),
            console=console,
        )
        self._progress.start()
        self._task_id = self._progress.add_task("Fetching movies", total=total)

    def on_movie_done(self) -> None:
        if self._progress and self._task_id is not None:
            self._progress.advance(self._task_id)

    def on_movies_done(self) -> None:
        if self._progress:
            self._progress.stop()
            self._progress = None
        console.print("[green]✓[/green] All movies fetched")


@click.command()
@click.option(
    "--max-connections",
    default=Config.MAX_CONNECTIONS,
    help=f"Maximum concurrent connections. (Default: {Config.MAX_CONNECTIONS})",
)
@click.option("--db-file", default=Config.DB_FILE, help=f"Path to the SQLite database. (Default: {Config.DB_FILE})")
def main(max_connections: int, db_file: str) -> None:
    """CSFD TOP 300 scrapper."""
    progress = RichFetchProgress()

    scrape_and_save(
        top_300_urls=Config.CSFD_TOP_300_URLS,
        db_file=db_file,
        max_connections=max_connections,
        progress=progress,
    )
    console.print(f"[green]✓[/green] Saved to {db_file}")


if __name__ == "__main__":
    main()  #  type: ignore
