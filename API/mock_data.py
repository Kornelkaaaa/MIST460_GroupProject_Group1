import os


def is_mock_mode() -> bool:
    return os.getenv("MOCK_MODE", "").lower() in ("1", "true", "yes")


VALIDATE_USER = [
    {"AppUserID": 1, "Fullname": "Alex Rivera"},
]

RECOMMENDATIONS = [
    {
        "GameID": 101,
        "GameTitle": "Echoes of Aether",
        "YearReleased": 2024,
        "AverageRating": 4.7,
        "StudioName": "Lumen Studios",
        "PrimaryGenre": "RPG",
        "CommunityCompletionPct": 62.5,
        "RecommendationReason": "Matches your preferences",
    },
    {
        "GameID": 102,
        "GameTitle": "Neon Drift",
        "YearReleased": 2023,
        "AverageRating": 4.4,
        "StudioName": "Pulse Games",
        "PrimaryGenre": "Racing",
        "CommunityCompletionPct": 78.0,
        "RecommendationReason": "Matches your preferences",
    },
    {
        "GameID": 103,
        "GameTitle": "Hollow Spire",
        "YearReleased": 2022,
        "AverageRating": 4.2,
        "StudioName": "Greyforge",
        "PrimaryGenre": "Action",
        "CommunityCompletionPct": 41.3,
        "RecommendationReason": "Matches your preferences",
    },
]

SEARCH_RESULTS = [
    {
        "GameID": 201,
        "GameTitle": "Open Horizon",
        "GameDescription": "A vast open-world survival adventure.",
        "YearReleased": 2024,
        "AverageRating": 4.6,
        "StudioName": "Skybound",
        "PrimaryGenre": "Adventure",
        "CompletionRatePct": 55.0,
        "AlreadyOwned": "No",
    },
    {
        "GameID": 202,
        "GameTitle": "Open World Tycoon",
        "GameDescription": "Build your empire across an open world.",
        "YearReleased": 2021,
        "AverageRating": 4.0,
        "StudioName": "Cog & Crown",
        "PrimaryGenre": "Strategy",
        "CompletionRatePct": 33.0,
        "AlreadyOwned": "Yes",
    },
]

NEXT_GAME_SUGGESTION = [
    {
        "GameID": 101,
        "GameTitle": "Echoes of Aether",
        "AverageRating": 4.7,
        "PrimaryGenre": "RPG",
        "Status": "Not Started",
        "HoursPlayed": 0.0,
        "SuggestionReason": "You own this but have not started it yet",
        "GamesYouHaveFinished": 4,
    },
]

DEVELOPER_ANALYTICS = {
    "summary": [
        {
            "GameTitle": "Echoes of Aether",
            "YearReleased": 2024,
            "LiveAverageRating": 4.7,
            "CompletionRatePct": 62.5,
            "TotalOwners": 124,
            "TotalFinished": 78,
            "CurrentlyPlaying": 31,
            "NotStarted": 15,
            "AvgHoursPlayed": 22.4,
            "TotalReviews": 88,
        }
    ],
    "sentiment": [
        {"SentimentBucket": "Positive (4.0 - 5.0)", "ReviewCount": 70, "AvgRating": 4.6},
        {"SentimentBucket": "Mixed (2.5 - 3.9)", "ReviewCount": 14, "AvgRating": 3.2},
        {"SentimentBucket": "Negative (0.0 - 2.4)", "ReviewCount": 4, "AvgRating": 1.8},
    ],
    "player_profile": [
        {
            "PreferredMode": "Single-Player",
            "PreferredDifficulty": "Hard",
            "PreferredPlayStyle": "Story",
            "PlayerCount": 60,
            "AvgHoursPlayed": 28.1,
            "AvgGamesFinishedByThisPlayerType": 5.4,
        },
        {
            "PreferredMode": "Co-op",
            "PreferredDifficulty": "Medium",
            "PreferredPlayStyle": "Casual",
            "PlayerCount": 22,
            "AvgHoursPlayed": 14.8,
            "AvgGamesFinishedByThisPlayerType": 3.1,
        },
    ],
}
