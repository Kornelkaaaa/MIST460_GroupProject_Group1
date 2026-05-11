"""
LLM-powered "game advisor" that turns raw vector-search results into a
ranked, explained recommendation.

Pattern mirrors a typical RAG flow:
  1. Caller has already done the embedding retrieval (top-N similar
     games with cosine distances).
  2. format_context() shapes those rows into a readable prompt block.
  3. advise() sends a system+human prompt to OpenAI with temperature=0
     so output is deterministic for testing.

The model is told to:
  - rank games from most to least relevant,
  - explain mechanical/thematic alignment for strong matches,
  - be honest about weak matches,
  - flag any game whose cosine distance is > 0.4,
  - cite each match score it discusses,
  - NOT invent content beyond what's in the provided descriptions/reviews,
  - tell the user to refine the query if nothing fits.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
_client: Optional[OpenAI] = None

ADVISOR_MODEL = "gpt-4o-mini"  # cheap, fast, deterministic enough at temp=0


def _openai() -> OpenAI:
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY missing in .env")
        _client = OpenAI(api_key=key)
    return _client


SYSTEM_PROMPT = """You are an expert game recommendation assistant.

You will receive a user's plain-English description of the kind of game
they want to play, plus a list of candidate games that semantically match
their query. The candidates were retrieved by a cosine-similarity vector
search over each game's description text and player reviews. Each
candidate carries a `Cosine distance` value (lower = more similar; 0.0 =
identical, ~1.0 = unrelated).

Your job:
  1. Assess each retrieved game against the user's query.
  2. Explain the mechanical and thematic alignment for strong matches.
  3. Be honest about weak matches — do not pretend a poor fit is good.
  4. Rank the games from most to least relevant.
  5. Do NOT invent content beyond what is in the provided text.
  6. If a game's cosine distance is above 0.4, flag it as a WEAK MATCH
     and briefly explain why it appeared anyway.
  7. If nothing fits well, suggest the user refine or broaden their query.

Cite each game's cosine distance as you discuss it. Use markdown
formatting (## headings per game, bullet points for alignment, bold for
the verdict). Keep each game's section to 2-4 short paragraphs.
"""


HUMAN_PROMPT_TEMPLATE = """User query:
{user_query}

Candidate games retrieved by vector search (n={game_count}):

{context}

Provide a ranked recommendation. Cite each cosine distance, flag any
weak matches above 0.4, and recommend the user refine their search if
none of the candidates feels right.
"""


def format_context(games: list[dict]) -> str:
    """Shape retrieved game rows into a readable block for the LLM prompt."""
    formatted = []
    for g in games:
        formatted.append(
            f"Game: {g.get('GameTitle')} ({g.get('YearReleased')}) — {g.get('StudioName')}\n"
            f"Average user rating: {g.get('AverageRating')}/5\n"
            f"Cosine distance: {float(g.get('Distance', 1.0)):.3f} "
            f"[lower = better, flag if above 0.4]\n"
            f"Closest matching text: {g.get('Evidence')}"
        )
    return "\n\n---\n\n".join(formatted)


def advise(user_query: str, games: list[dict]) -> str:
    """Run the system+human prompt through gpt-4o-mini and return the
    advisor's markdown response."""
    if not games:
        return (
            "No games matched closely enough to advise on. Try refining "
            "your query with more concrete adjectives."
        )

    human = HUMAN_PROMPT_TEMPLATE.format(
        user_query=user_query.strip(),
        game_count=len(games),
        context=format_context(games),
    )

    response = _openai().chat.completions.create(
        model=ADVISOR_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": human},
        ],
    )
    return response.choices[0].message.content or ""