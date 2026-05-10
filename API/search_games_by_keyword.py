from typing import Any, Optional

import pymssql

from get_db_connection import get_db_connection


def _to_float(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def search_games_by_keyword(keyword: str, gamer_id: Optional[int] = None, top_n: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        "EXEC sp_SearchGamesByKeyword %s, %s, %d",
        (keyword, gamer_id, top_n),
    )

    try:
        rows = cursor.fetchall()
    except pymssql.Error:
        rows = []

    conn.close()

    results = [
        {
            "GameID": row["GameID"],
            "GameTitle": row["GameTitle"],
            "GameDescription": row["GameDescription"],
            "YearReleased": row["YearReleased"],
            "AverageRating": _to_float(row["AverageRating"]),
            "StudioName": row["StudioName"],
            "PrimaryGenre": row["PrimaryGenre"],
            "CompletionRatePct": _to_float(row["CompletionRatePct"]),
            "AlreadyOwned": row["AlreadyOwned"],
        }
        for row in rows
    ]
    return {"data": results}
