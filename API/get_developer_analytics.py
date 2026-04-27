import pymssql

from get_db_connection import get_db_connection
from mock_data import DEVELOPER_ANALYTICS, is_mock_mode


def get_developer_analytics(game_id: int, developer_id: int):
    if is_mock_mode():
        return DEVELOPER_ANALYTICS

    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        "EXEC sp_GetDeveloperAnalytics %d, %d",
        (game_id, developer_id),
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
