import os


class Config:
    DB_FILE = os.environ.get("DB_FILE", "movies.db")

    CSFD_DOMAIN = "https://www.csfd.cz"
    CSFD_TOP_300_URLS = [
        "https://www.csfd.cz/zebricky/filmy/nejlepsi/",
        "https://www.csfd.cz/zebricky/filmy/nejlepsi/?from=100",
        "https://www.csfd.cz/zebricky/filmy/nejlepsi/?from=200",
    ]

    # 4 is quite conservative number, 20 usually works well, but if speed is not an issue, 4 should be safe
    MAX_CONNECTIONS = int(os.environ.get("MAX_CONNECTIONS", 4))
