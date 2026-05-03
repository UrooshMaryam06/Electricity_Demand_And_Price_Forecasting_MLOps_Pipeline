FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app-frontend/assets ./app-frontend/assets
COPY artifacts ./artifacts
COPY app-monitoring ./app-monitoring

WORKDIR /app/app-monitoring

EXPOSE 8502

CMD ["streamlit", "run", "Home.py", "--server.port=8502", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
