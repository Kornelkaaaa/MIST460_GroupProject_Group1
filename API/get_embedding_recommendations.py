import os
from typing import Any, Optional

import pymssql
from dotenv import load_dotenv
from openai import OpenAI

from get_db_connection import get_db_connection
from game_advisor import advise


load_dotenv()
_client: Optional[OpenAI] = None


def _openai() -> OpenAI:
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY missing in .env")
        _client = OpenAI(api_key=key)
    return _client


def _embed(text: str) -> list[float]:
    resp = _openai().embeddings.create(
        model="text-embedding-3-small", input=text
    )
    return resp.data[0].embedding


def _to_float(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def _vec_literal(vec: list[float]) -> str:
    return "[" + ",".join(f"{x:.7f}" for x in vec) + "]"


def get_embedding_recommendations(
    query: str,
    gamer_id: Optional[int] = None,
    include_advisor: bool = True,
):
    if not query.strip():
        return {"data": [], "error": "Query cannot be empty."}

    try:
        embedding = _embed(query.strip())
    except Exception as e:
        return {"error": f"Embedding failed: {e}"}

    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    # We DECLARE @v VECTOR(1536) on the server side, then EXEC the SP
    # with the typed variable. pymssql parameters become literals here,
    # which is fine for an embedding the API itself just computed.
    sql = (
        "DECLARE @v VECTOR(1536) = CAST(%s AS VECTOR(1536)); "
        "EXEC sp_GetEmbeddingRecommendations "
        "    @QueryEmbedding = @v, @GamerID = %s;"
    )

    try:
        cursor.execute(sql, (_vec_literal(embedding), gamer_id))
        rows = cursor.fetchall()
    except pymssql.Error as e:
        conn.close()
        return {"error": str(e)}

    conn.close()

    results = [
        {
            "GameID": r["GameID"],
            "GameTitle": r["GameTitle"],
            "YearReleased": r["YearReleased"],
            "AverageRating": _to_float(r["AverageRating"]),
            "StudioName": r["StudioName"],
            "Evidence": r["Evidence"],
            "Distance": _to_float(r["Distance"]),
        }
        for r in rows
    ]

    advisor_text = ""
    if include_advisor and results:
        try:
            advisor_text = advise(query, results)
        except Exception as e:
            advisor_text = f"_Advisor unavailable: {e}_"

    return {"data": results, "advisor": advisor_text}
