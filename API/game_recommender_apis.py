from typing import Optional

from fastapi import FastAPI

from validate_user import validate_user
from get_recommendations import get_recommendations
from search_games_by_keyword import search_games_by_keyword
from get_next_game_suggestion import get_next_game_suggestion
from get_developer_analytics import get_developer_analytics


app = FastAPI()


@app.get("/validate_user/")
def validate_user_endpoint(username: str, password: str):
    return validate_user(username, password)


@app.get("/get_recommendations/")
def get_recommendations_endpoint(gamer_id: int, top_n: int = 6):
    return get_recommendations(gamer_id, top_n)


@app.get("/search_games_by_keyword/")
def search_games_by_keyword_endpoint(
    keyword: str,
    gamer_id: Optional[int] = None,
    top_n: int = 10,
):
    return search_games_by_keyword(keyword, gamer_id, top_n)


@app.get("/get_next_game_suggestion/")
def get_next_game_suggestion_endpoint(gamer_id: int):
    return get_next_game_suggestion(gamer_id)


@app.get("/get_developer_analytics/")
def get_developer_analytics_endpoint(game_title: str, developer_id: int):
    return get_developer_analytics(game_title, developer_id)
