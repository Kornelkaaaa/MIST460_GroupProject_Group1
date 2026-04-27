from typing import Optional

import pymssql

from get_db_connection import get_db_connection
from mock_data import SEARCH_RESULTS, is_mock_mode


def search_games_by_keyword(keyword: str, gamer_id: Optional[int] = None, top_n: int = 10):
    if is_mock_mode():
        kw = (keyword or "").lower()
        filtered = [
            r for r in SEARCH_RESULTS
            if kw in r["GameTitle"].lower()
            or kw in r["GameDescription"].lower()
            or kw in r["PrimaryGenre"].lower()
            or kw in r["StudioName"].lower()
        ]
        return {"data": (filtered or SEARCH_RESULTS)[:top_n]}

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
            "AverageRating": float(row["AverageRating"]) if row["AverageRating"] is not None else None,
            "StudioName": row["StudioName"],
            "PrimaryGenre": row["PrimaryGenre"],
            "CompletionRatePct": float(row["CompletionRatePct"]) if row["CompletionRatePct"] is not None else None,
            "AlreadyOwned": row["AlreadyOwned"],
        }
        for row in rows
    ]
    return {"data": results}
