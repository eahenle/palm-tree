#!/bin/bash

cd /home/pi/auth-bot
git fetch origin main

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "🔄 Update available. Pulling changes..."
    git pull origin main --rebase
    docker-compose build
    docker-compose up -d
    echo "✅ Updated and restarted bot at $(date)"
else
    echo "🟢 No update needed at $(date)"
fi
