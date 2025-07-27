#!/bin/bash
cd /home/pi/auth-bot
git fetch
if [ "$(git rev-parse HEAD)" != "$(git rev-parse @{u})" ]; then
  echo "🔄 Updates found. Pulling and rebuilding..."
  git pull --rebase
  docker-compose build
  docker-compose up -d
else
  echo "✅ No updates needed."
fi
