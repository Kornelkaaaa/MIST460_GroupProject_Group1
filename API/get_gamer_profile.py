from typing import Any, Optional

import pymssql

from get_db_connection import get_db_connection


def _to_float(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def get_gamer_profile(gamer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    cursor.execute(
        "SELECT u.AppUserID, u.FirstName, u.LastName, u.Email, u.Phone, "
        "       g.PreferredGenres, g.PreferredDifficulty, "
        "       g.PreferredPlayStyle, g.PreferredMode, g.AvailablePlayTime "
        "FROM AppUser u "
        "    JOIN Gamer g ON g.GamerID = u.AppUserID "
        "WHERE u.AppUserID = %d",
        (gamer_id,),
    )

    try:
        rows = cursor.fetchall()
    except pymssql.Error:
        rows = []

    conn.close()

    if not rows:
        return {"data": None}

    row = rows[0]
    return {
        "data": {
            "AppUserID": row["AppUserID"],
            "FirstName": row["FirstName"],
            "LastName": row["LastName"],
            "Email": row["Email"],
            "Phone": row["Phone"],
            "PreferredGenres": row["PreferredGenres"],
            "PreferredDifficulty": row["PreferredDifficulty"],
            "PreferredPlayStyle": row["PreferredPlayStyle"],
            "PreferredMode": row["PreferredMode"],
            "AvailablePlayTime": _to_float(row["AvailablePlayTime"]),
        }
    }
