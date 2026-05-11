from typing import Optional

from fastapi import FastAPI

from validate_user import validate_user
from get_recommendations import get_recommendations
from search_games_by_keyword import search_games_by_keyword
from get_next_game_suggestion import get_next_game_suggestion
from get_developer_analytics import get_developer_analytics
from register_gamer import register_gamer
from add_game_to_library import add_game_to_library
from update_game_status import update_game_status
from submit_review import submit_review
from full_gamer_onboarding import full_gamer_onboarding
from get_gamer_library import get_gamer_library
from get_all_games import get_all_games
from get_developer_games import get_developer_games
from remove_game_from_library import remove_game_from_library
from update_review import update_review
from delete_review import delete_review
from update_gamer_profile import update_gamer_profile
from get_gamer_profile import get_gamer_profile
from get_embedding_recommendations import get_embedding_recommendations


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


@app.get("/get_gamer_library/")
def get_gamer_library_endpoint(gamer_id: int):
    return get_gamer_library(gamer_id)


@app.get("/get_all_games/")
def get_all_games_endpoint():
    return get_all_games()


@app.get("/get_developer_games/")
def get_developer_games_endpoint(developer_id: int):
    return get_developer_games(developer_id)


@app.get("/remove_game_from_library/")
def remove_game_from_library_endpoint(gamer_id: int, game_title: str):
    return remove_game_from_library(gamer_id, game_title)


@app.get("/update_review/")
def update_review_endpoint(
    gamer_id: int,
    game_title: str,
    rating: float,
    review_text: Optional[str] = None,
):
    return update_review(gamer_id, game_title, rating, review_text)


@app.get("/delete_review/")
def delete_review_endpoint(gamer_id: int, game_title: str):
    return delete_review(gamer_id, game_title)


@app.get("/get_gamer_profile/")
def get_gamer_profile_endpoint(gamer_id: int):
    return get_gamer_profile(gamer_id)


@app.get("/get_embedding_recommendations/")
def get_embedding_recommendations_endpoint(
    query: str,
    gamer_id: Optional[int] = None,
    include_advisor: bool = True,
):
    return get_embedding_recommendations(query, gamer_id, include_advisor)


@app.get("/update_gamer_profile/")
def update_gamer_profile_endpoint(
    gamer_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    preferred_genres: Optional[str] = None,
    preferred_difficulty: Optional[str] = None,
    preferred_play_style: Optional[str] = None,
    preferred_mode: Optional[str] = None,
    available_play_time: Optional[float] = None,
):
    return update_gamer_profile(
        gamer_id,
        first_name,
        last_name,
        phone,
        preferred_genres,
        preferred_difficulty,
        preferred_play_style,
        preferred_mode,
        available_play_time,
    )


@app.get("/register_gamer/")
def register_gamer_endpoint(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: Optional[str] = None,
    preferred_genres: Optional[str] = None,
    preferred_difficulty: Optional[str] = None,
    preferred_play_style: Optional[str] = None,
    preferred_mode: Optional[str] = None,
    available_play_time: Optional[float] = None,
):
    return register_gamer(
        first_name,
        last_name,
        email,
        password,
        phone,
        preferred_genres,
        preferred_difficulty,
        preferred_play_style,
        preferred_mode,
        available_play_time,
    )


@app.get("/add_game_to_library/")
def add_game_to_library_endpoint(gamer_id: int, game_title: str):
    return add_game_to_library(gamer_id, game_title)


@app.get("/update_game_status/")
def update_game_status_endpoint(
    gamer_id: int,
    game_title: str,
    new_status: str,
    hours_played: Optional[float] = None,
):
    return update_game_status(gamer_id, game_title, new_status, hours_played)


@app.get("/submit_review/")
def submit_review_endpoint(
    gamer_id: int,
    game_title: str,
    rating: float,
    review_text: Optional[str] = None,
):
    return submit_review(gamer_id, game_title, rating, review_text)


@app.get("/full_gamer_onboarding/")
def full_gamer_onboarding_endpoint(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: Optional[str] = None,
    preferred_genres: Optional[str] = None,
    preferred_difficulty: Optional[str] = None,
    preferred_play_style: Optional[str] = None,
    preferred_mode: Optional[str] = None,
    available_play_time: Optional[float] = None,
    owned_game_titles: Optional[str] = None,
):
    return full_gamer_onboarding(
        first_name,
        last_name,
        email,
        password,
        phone,
        preferred_genres,
        preferred_difficulty,
        preferred_play_style,
        preferred_mode,
        available_play_time,
        owned_game_titles,
    )
