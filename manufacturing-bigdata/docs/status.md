# Implementation status

## Runnable now

- Core API endpoints for products, machines, inventory, forecasts, production requirements, schedules, news-event impact, what-if simulation and machine failure rescheduling.
- Deterministic moving-average forecasts and confidence/relevance/severity-based event adjustments (capped; no LLM-generated quantities).
- Heuristic machine-compatible scheduler with machine unavailability, simple capacity and material limits.
- Synthetic CSV data generation with scalable streaming writes.
- Streamlit dashboard source, optional GDELT ingestion, optional OpenRouter JSON-schema client, optional PySpark batch ETL and Kafka/Spark streaming examples.
- PostgreSQL schema and Docker Compose starter for the web app plus PostgreSQL.

## Not represented as complete

- OpenRouter live extraction was not called; the credential pasted in chat is not stored or used. Rotate it before use.
- HDFS, Kafka, Spark, Airflow, PostgreSQL persistence and the dashboard have not been launched in this sandbox; the local environment has no Docker executable. Compose only defines the lightweight API/dashboard/Postgres starter.
- Optional OR-Tools CP-SAT scheduling enforces product-machine compatibility, non-overlap, work-hour capacity, material caps and shortage penalties; without OR-Tools the API falls back to the greedy demo scheduler. Planned maintenance windows, due-date lateness, and explicit sequence-dependent changeover optimization are not yet modeled.
- M5 and AI4I external datasets are not bundled; generated internal factory records are simulated. GDELT can be queried using the optional ingestion script.
- The tree-model training script is included but was not executed here because scikit-learn is not installed in the sandbox; install `requirements.txt` to run it.
- Multi-million-row benchmark results are not fabricated; `docs/evaluation.md` describes how to run and report them on target hardware.
