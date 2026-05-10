from typing import Optional

import pymssql

from get_db_connection import get_db_connection


def update_game_status(
    gamer_id: int,
    game_title: str,
    new_status: str,
    hours_played: Optional[float] = None,
):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        cursor.execute(
            "EXEC sp_UpdateGameStatus "
            "@GamerID=%d, @GameTitle=%s, @NewStatus=%s, @HoursPlayed=%s",
            (gamer_id, game_title, new_status, hours_played),
        )
        rows = cursor.fetchall()
        conn.commit()
    except pymssql.Error as e:
        conn.rollback()
        conn.close()
        return {"error": str(e)}

    conn.close()

    return {"data": rows[0] if rows else {}}
