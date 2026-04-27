import pymssql

from get_db_connection import get_db_connection
from mock_data import VALIDATE_USER, is_mock_mode


def validate_user(username: str, password: str):
    if is_mock_mode():
        return {"data": VALIDATE_USER}

    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute("EXEC procValidateUser %s, %s", (username, password))

    try:
        rows = cursor.fetchall()
    except pymssql.Error:
        rows = []

    conn.close()

    results = [
        {
            "AppUserID": row["AppUserID"],
            "Fullname": row["Fullname"],
        }
        for row in rows
    ]
    return {"data": results}
