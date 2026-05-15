FROM python:3.14.3-slim

WORKDIR /app

RUN useradd -m appuser

RUN pip install --no-cache-dir asyncio

COPY app/worker/ .

USER appuser

CMD ["python", "worker.py"]
