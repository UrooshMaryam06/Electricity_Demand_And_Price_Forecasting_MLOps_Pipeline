FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main_new_v2.py ./
COPY energy_dataset.csv ./
COPY artifacts ./artifacts
COPY app-api ./app-api

WORKDIR /app/app-api

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
