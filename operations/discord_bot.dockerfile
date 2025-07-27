FROM python:3.11-slim

# Install curl (for GitHub trigger)
RUN apt-get update && apt-get install -y curl && apt-get clean

# Create working directory
WORKDIR /app

# Copy code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (will be overridden by .env or runtime)
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "auth_update_bot.py"]
# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install build tools and git
RUN apt-get update && \
    apt-get install -y git build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY . .

# Entrypoint
CMD ["python", "discord_bot.py"]
