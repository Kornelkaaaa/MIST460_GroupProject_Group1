import pymssql

from get_db_connection import get_db_connection


def add_game_to_library(gamer_id: int, game_title: str):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        cursor.execute(
            "EXEC sp_AddGameToLibrary @GamerID=%d, @GameTitle=%s",
            (gamer_id, game_title),
        )
        rows = cursor.fetchall()
        conn.commit()
    except pymssql.Error as e:
        conn.rollback()
        conn.close()
        return {"error": str(e)}

    conn.close()

    return {"data": rows[0] if rows else {}}
