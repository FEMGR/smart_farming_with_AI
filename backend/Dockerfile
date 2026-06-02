FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

WORKDIR /app

COPY backend/requirements.txt .

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client swi-prolog-nox \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --disable-pip-version-check --timeout 120 --retries 5 -r requirements.txt

COPY backend ./backend
COPY logic_companion_planting ./logic_companion_planting

EXPOSE 8000

ENTRYPOINT ["sh", "/app/backend/entrypoint.sh"]
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
