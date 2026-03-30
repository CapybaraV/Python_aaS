FROM python:3.13-slim

WORKDIR /scripts

COPY scripts/ .

EXPOSE 8000

CMD ["python", "-m", "http.server", "8000"]