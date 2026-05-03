# Electricity Demand & Price Forecasting MLOps Pipeline
It is an end-to-end machine learning system that predicts electricity demand and prices using historical and weather data, and continuously updates the model using MLOps practices like deployment, monitoring, and retraining

## Project Layout

- `app-api/` FastAPI service that serves the trained models and health checks.
- `app-frontend/` Streamlit dashboard for forecasts, comparison, exploration, and API testing.
- `app-monitoring/` Streamlit monitoring view for experiment logs and pipeline metadata.

## Run

### 1. Train and generate artifacts

Run the notebook or the training script first so `artifacts/` is populated.

```bash
python modeltraining.py
```

If you use the notebook workflow, run the final log cell in `colab_modeltraining_v4.ipynb` so the experiment log files are created.

### 2. Start the API

```bash
cd app-api
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API is available at `http://localhost:8000`.

### 3. Start the main frontend

```bash
cd app-frontend
$env:API_BASE_URL="http://localhost:8000"
streamlit run Home.py --server.port 8501
```

The dashboard is available at `http://localhost:8501`.

The `Home` page includes a sidebar option for `Experiment Logs`, so the log output stays inside the main frontend.

### 4. Start the monitoring app

```bash
cd app-monitoring
streamlit run Home.py --server.port 8502
```

The monitoring view is available at `http://localhost:8502`.

This is optional now. The same log data is also shown inside the main frontend Home page.

### 5. Optional Docker Compose startup

```bash
docker compose up --build
```

This starts all three services together:

- API on `8000`
- Frontend on `8501`
- Monitoring on `8502`

## Verify

After startup, check these in order:

1. Open `http://localhost:8000/health` and confirm the API returns `status: ok`.
2. Open the Streamlit frontend at `http://localhost:8501` and confirm the overview page shows the API status, model snapshot, and experiment log summary.
3. Open the monitoring app at `http://localhost:8502` and confirm it displays `experiment_log.json`, the model metrics table, and pipeline metadata.
4. If you use Docker Compose, confirm the frontend resolves the API through the `api` service name and not `localhost`.
