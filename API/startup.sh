#!/bin/sh
gunicorn -w 4 -k uvicorn.workers.UvicornWorker game_recommender_apis:app
