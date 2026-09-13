# Build context is the repo root (see docker-compose.yml / `docker build -f backend/Dockerfile .`)
# so that data/ can be copied in alongside the backend code.
FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY data ./data

ENV CORRIDORS_FILE=/app/data/corridors.json \
    EVENTS_CALENDAR_FILE=/app/data/events_calendar.csv \
    CASE_STUDY_FILE=/app/data/case_study_sep11_2026.md \
    PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
