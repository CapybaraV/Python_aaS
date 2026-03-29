FROM python:3.13-slim

WORKDIR /app

COPY scripts ./scripts

EXPOSE 8000

CMD ["python", "-m", "http.server", "8000", "--directory", "/app"]