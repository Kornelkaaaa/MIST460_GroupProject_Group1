import os

import pymssql
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    return pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database,
        port=1433,
        tds_version="7.4",
    )
