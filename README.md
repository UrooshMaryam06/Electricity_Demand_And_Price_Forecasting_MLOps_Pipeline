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

### 6. CI/CD and DeepChecks

The repository now includes `.github/workflows/ci.yml`, which:

- installs dependencies
- runs `python -m compileall` and `pytest`
- runs `scripts/run_deepchecks.py`
- builds both Docker images
- sends a Discord notification with the final job status

To enable Discord alerts, create a GitHub Actions secret named `DISCORD_WEBHOOK_URL` and store your webhook URL there.

To run the DeepChecks validation locally:

```bash
python scripts/run_deepchecks.py --data energy_dataset.csv --output-dir artifacts/deepchecks
```

## Verify

After startup, check these in order:

1. Open `http://localhost:8000/health` and confirm the API returns `status: ok`.
2. Open the Streamlit frontend at `http://localhost:8501` and confirm the overview page shows the API status, model snapshot, and experiment log summary.
3. Open the monitoring app at `http://localhost:8502` and confirm it displays `experiment_log.json`, the model metrics table, and pipeline metadata.
4. If you use Docker Compose, confirm the frontend resolves the API through the `api` service name and not `localhost`.

---

## API: dataset upload and Prefect notifications

You can upload a new CSV dataset to the running API without restarting the server.

- Endpoint: `POST /upload/dataset` (multipart/form-data)
- Form key: `file` — the CSV file to upload
- Query param: `replace=true|false` (default `true`) — whether to attempt replacing the in-memory historical dataset

Example (curl):

```bash
curl -X POST -F "file=@energy_dataset.csv" http://localhost:8000/upload/dataset
```

Admin token (optional):
- If you set the environment variable `ADMIN_UPLOAD_TOKEN` on the server, uploads will require this token.
- Provide it via the header `X-ADMIN-TOKEN` or the `token` query param.

Example with header:

```bash
export ADMIN_UPLOAD_TOKEN="s3cr3t"
curl -X POST -H "X-ADMIN-TOKEN: s3cr3t" -F "file=@energy_dataset.csv" http://localhost:8000/upload/dataset
```

Validation: the upload endpoint performs a minimal validation before replacing the in-memory dataset. The CSV must contain at least these columns: `time`, `total load actual`, `price actual`. If those columns are missing the file will still be saved to disk but `HIST_DF` will not be replaced and the endpoint returns a warning.

Prefect -> Discord notifications:
- The Prefect flow will post a short success or failure message to a Discord webhook when the environment variable `DISCORD_WEBHOOK_URL` is set.
- To enable locally, export the variable before running the Prefect flow:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/xxxxx/xxxxx"
python -c "from train_pipeline import prefect_build_pipeline; prefect_build_pipeline('energy_dataset.csv','artifacts')"
```

Notes:
- The notification helper is best-effort: webhook failures are swallowed so the flow doesn't fail because of notification errors.
- If you prefer stronger validation of CSV column names, or different required fields, we can extend the validator.
