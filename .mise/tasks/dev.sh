#!/usr/bin/env bash
#MISE description="Start the app"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
