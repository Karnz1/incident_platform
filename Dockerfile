FROM python:3.14.3-slim

WORKDIR /app

RUN useradd -m appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && pip check

COPY app/ .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; resp = urllib.request.urlopen('http://localhost:8000/health'); assert resp.status == 200"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
