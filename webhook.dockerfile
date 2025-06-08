# File: webhook/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask
ENV PYTHONUNBUFFERED=1
CMD ["python", "webhook.py"]
