FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim

RUN groupadd --system app && \
useradd --system --no-create-home --shell /bin/false --group app appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

COPY --from=builder /usr/local/bin /usr/local/bin/

COPY ./pipelinedquotes/main.py .

RUN chown -R appuser:app /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=3s --start-period=5s --retries=3 CMD ["python", "-c","import requests; requests.get('http://localhost:8000/health').raise_for_status()"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
