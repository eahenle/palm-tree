#!/bin/bash
docker build -t blog-bot .
docker run -d \
  --name blog-bot \
  --restart unless-stopped \
  -v $(pwd)/.agent_cache:/app/.agent_cache \
  --env-file .env \
  blog-bot
