#!/usr/bin/env sh
set -eu

docker compose up --build -d
echo "AlphaRadar is running at http://localhost:8000"
