| Entity | Key fields | Source/status |
|---|---|---|
| products | product_id, category, processing time, material/unit | Synthetic |
| machines | machine_id, capacity, efficiency, supported products | Synthetic |
| inventory | current, reserved, safety, incoming quantities | Synthetic |
| customer_orders | order, product, quantity, priority, promise date | Synthetic |
| production_history | machine, product, planned/completed quantity, downtime | Synthetic |
| machine_events | timestamp, temperature, vibration, pressure, status | Synthetic sensor replay |
| news_events | classification, directions, severity, confidence, URL | Optional user-supplied/news input; LLM off by default |
| forecast | base demand, adjustment %, adjusted units, horizon | Derived |
| schedule | product, machine, quantity, interval, status | Derived heuristic schedule |
