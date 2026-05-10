import pymssql

from get_db_connection import get_db_connection


def get_developer_analytics(game_title: str, developer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        "EXEC sp_GetDeveloperAnalytics %s, %d",
        (game_title, developer_id),
    )

    summary = []
    sentiment = []
    player_profile = []

    try:
        summary = cursor.fetchall()
        if cursor.nextset():
            sentiment = cursor.fetchall()
        if cursor.nextset():
            player_profile = cursor.fetchall()
    except pymssql.Error:
        pass

    conn.close()

    return {
        "summary": summary,
        "sentiment": sentiment,
        "player_profile": player_profile,
    }
