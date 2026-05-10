import pymssql

from get_db_connection import get_db_connection


def get_next_game_suggestion(gamer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute("EXEC sp_GetNextGameSuggestion %d", (gamer_id,))

    try:
        rows = cursor.fetchall()
    except pymssql.Error:
        rows = []

    conn.close()

    results = []
    for row in rows:
        results.append(
            {
                "GameID": row.get("GameID"),
                "GameTitle": row.get("GameTitle"),
                "AverageRating": float(row["AverageRating"]) if row.get("AverageRating") is not None else None,
                "PrimaryGenre": row.get("PrimaryGenre"),
                "Status": row.get("Status"),
                "HoursPlayed": float(row["HoursPlayed"]) if row.get("HoursPlayed") is not None else None,
                "SuggestionReason": row.get("SuggestionReason"),
                "GamesYouHaveFinished": row.get("GamesYouHaveFinished"),
            }
        )
    return {"data": results}
