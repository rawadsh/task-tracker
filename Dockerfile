# ---- Build stage: install dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Runtime stage ----
FROM python:3.11-slim

RUN useradd --create-home --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /root/.local /home/app/.local
COPY backend/app ./app

RUN chown -R app:app /home/app/.local

ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

EXPOSE 8000

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
