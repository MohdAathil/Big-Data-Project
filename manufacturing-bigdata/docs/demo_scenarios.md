# Demo scenarios

Start the API with `uvicorn api.main:app --reload`, then use `/docs` or the dashboard.

1. **Normal operation** — GET `/forecast`, `/production-requirements`, `/schedule`, `/kpis`.
2. **Demand increase** — POST `/simulate/scenario` with `{"demand_change_pct":20,"failed_machines":[],"inventory_adjustment":{}}`.
3. **Failure recovery** — POST `/simulate/machine-failure` with `{"machine_id":"M002"}`; verify the returned schedule excludes M002.
4. **External event** — POST `/news-events` with `{"summary":"Electronics manufacturing investment increases","demand_direction":"positive","severity":"high","relevance_score":0.9,"confidence":0.85,"source_url":"https://example.org/article"}`; GET `/forecast` and compare adjustment fields.
5. **Inventory what-if** — POST `/simulate/scenario` with `{"demand_change_pct":0,"failed_machines":[],"inventory_adjustment":{"P001":-100}}`.

All payloads above are illustrative prototype scenarios, not live operational advice.
