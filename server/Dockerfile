FROM python:3.13-slim

WORKDIR /app

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ../proto/service.proto /app/proto/

COPY server.py .
COPY executor.py .
COPY script_executor.py .

RUN python -m grpc_tools.protoc \
    -I/proto \
    --python_out=/app \
    --grpc_python_out=/app \
    /proto/service.proto

EXPOSE 50051

CMD ["python", "-u", "server.py"]