FROM python:3.13-slim

# Docker CLI
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY service_pb2.py .
COPY service_pb2_grpc.py .

COPY server.py .
COPY executor.py .

COPY proto/ ./proto/

RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=/app \
    --grpc_python_out=/app \
    ./proto/service.proto

EXPOSE 50051

CMD ["python", "-u", "server.py"]