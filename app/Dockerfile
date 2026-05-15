FROM python:3.14.3-slim

WORKDIR /src

RUN useradd -m appuser

RUN pip install --no-cache-dir asyncio \
psycopg[binary] \
psycopg-pool \
redis \
dotenv \
pydantic 

COPY worker/ ./app/worker/

COPY api/ ./app/api/

ENV PYTHONPATH=/src

USER appuser

CMD ["python", "-m", "app.worker.worker"]
