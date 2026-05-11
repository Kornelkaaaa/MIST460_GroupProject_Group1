"""
Populate the Chunks table with 1536-dim OpenAI embeddings of every
GameDescription and GamerReview.

Run after re-seeding the database:
    python API/ingest_embeddings.py

Requires OPENAI_API_KEY in API/.env.

The script is idempotent — it truncates Chunks first, then re-inserts.
For a class-sized catalog (~17 games + a handful of reviews) the
whole job takes a few seconds and costs well under a cent.
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from get_db_connection import get_db_connection


EMBEDDING_MODEL = "text-embedding-3-small"   # 1536 dimensions
BATCH_SIZE = 64                              # OpenAI accepts up to ~2048


def embed_texts(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Batch-embed a list of strings."""
    if not texts:
        return []
    out: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        resp = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        out.extend([d.embedding for d in resp.data])
    return out


def vec_literal(vec: list[float]) -> str:
    """Format a Python float list as the JSON array literal SQL Server's
    VECTOR type accepts."""
    return "[" + ",".join(f"{x:.7f}" for x in vec) + "]"


def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("OPENAI_API_KEY missing in .env")

    client = OpenAI(api_key=api_key)
    conn = get_db_connection()
    cur = conn.cursor(as_dict=True)

    print("Truncating Chunks…")
    cur.execute("DELETE FROM Chunks;")

    # Collect source texts
    cur.execute(
        "SELECT GameID, GameTitle, GameDescription "
        "FROM Game WHERE GameDescription IS NOT NULL"
    )
    games = cur.fetchall()

    cur.execute(
        "SELECT gr.GameID, g.GameTitle, gr.ReviewText "
        "FROM GamerReview gr JOIN Game g ON gr.GameID = g.GameID "
        "WHERE gr.ReviewText IS NOT NULL AND LEN(gr.ReviewText) > 0"
    )
    reviews = cur.fetchall()

    print(f"  {len(games)} game descriptions, {len(reviews)} reviews")

    # Build the parallel arrays we send to OpenAI
    sources: list[tuple[int, str]] = []   # (GameID, text)
    for g in games:
        sources.append(
            (g["GameID"], f"{g['GameTitle']}. {g['GameDescription']}")
        )
    for r in reviews:
        sources.append(
            (r["GameID"], f"Review of {r['GameTitle']}: {r['ReviewText']}")
        )

    print(f"Embedding {len(sources)} chunks with {EMBEDDING_MODEL}…")
    embeddings = embed_texts(client, [t for _, t in sources])

    print("Inserting into Chunks…")
    for (gid, text), emb in zip(sources, embeddings):
        cur.execute(
            "INSERT INTO Chunks (GameChunk, ChunkEmbedding, GameID) "
            "VALUES (%s, CAST(%s AS VECTOR(1536)), %d)",
            (text, vec_literal(emb), gid),
        )

    conn.commit()

    cur.execute("SELECT COUNT(*) AS n FROM Chunks")
    total = cur.fetchone()["n"]
    print(f"Done. Chunks now contains {total} rows.")

    conn.close()


if __name__ == "__main__":
    main()
