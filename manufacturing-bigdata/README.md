# Demand-Driven Smart Manufacturing — Prototype

A staged, local-first prototype for demand forecasting, deterministic news-event adjustments, production requirements, constrained scheduling, failure rescheduling, and an API/dashboard. Synthetic data is explicitly labeled as simulated. The OpenRouter adapter is optional and never contains credentials.

## What's implemented

- Synthetic factory master data, orders, inventory, production history, maintenance, and machine events, generated as CSV at configurable scale.
- Moving-average baseline and optional scikit-learn tree model; time-ordered holdout and MAE/RMSE/sMAPE.
- Strictly deterministic event adjustment: structured event relevance/severity adjusts the base forecast within configurable caps. LLM output never sets quantities or schedules.
- Production requirements using demand + safety stock − available inventory − planned/incoming production (clamped to zero).
- Compatibility, machine availability, work-hour and material-aware schedule generation, with failure rescheduling.
- FastAPI endpoints and a Streamlit dashboard; Docker Compose starter for the app and PostgreSQL, plus optional integration examples.
- Optional OpenRouter event-extraction adapter driven by `OPENROUTER_API_KEY`; never use the credential previously pasted into chat. Revoke/rotate it before configuring a fresh key.

## Quick start (local)

```bash
cd manufacturing-bigdata
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m data_generator.generate --orders 2000 --sensor-events 10000
uvicorn api.main:app --reload
# another terminal
streamlit run dashboard/app.py
```

API: http://127.0.0.1:8000/docs  | Dashboard: http://127.0.0.1:8501

Run checks: `python -m unittest discover -s tests -v`

## Docker

After copying `.env.example` to `.env`, `docker compose up --build` starts the API, dashboard, and PostgreSQL. Full HDFS/Spark/Kafka/Airflow services are intentionally not included in the default Compose file: those images consume substantial resources and need environment-specific tuning. A deployment expansion plan is in `docs/architecture.md`.

## Useful commands

```bash
python -m data_generator.generate --scale small  # 100k orders, 250k sensor events
python -m data_generator.generate --scale medium # 1M orders, 2M sensor events
python -m spark.batch_etl --input data/raw --output data/processed # requires PySpark
python -m kafka.simulate_failure M002              # POSTs a failure to the API
```

For the optional distributed Python adapters, install `pip install -r requirements-bigdata.txt` in addition to the base requirements.

Use `.env.example` as a template; copy to `.env` and set a **newly rotated** API key only if you explicitly enable live news extraction. Do not commit `.env`.

## Important scope and assumptions

This is a functional educational prototype, not a production manufacturing execution system. It uses deterministic synthetic data, a simple greedy scheduler (with optional OR-Tools CP-SAT enhancement planned as an extension), and in-memory API state. PostgreSQL, HDFS, Kafka, Spark, Airflow and production-grade persistence/monitoring need deployment-specific setup. The generator supports large volumes using streaming writes; do not generate multi-million-row CSVs unless disk space is available.

The specification's production equation is interpreted with conventional inventory arithmetic: safety stock is an additional target, so it is added to demand before subtracting available stock and planned/incoming supply. This avoids the counterintuitive result of reducing production when safety stock rises.
