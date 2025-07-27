#!/bin/bash

# Build the Docker image
docker build -t auth-bot .

docker-compose up -d --build

# Run the container with your .env file
docker run -d --restart=unless-stopped --env-file .env --name auth-bot auth-bot
