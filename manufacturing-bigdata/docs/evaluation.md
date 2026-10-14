# Evaluation plan and local demo baseline

The current prototype's tests validate deterministic logic and schedule feasibility properties; they are not a claim of business forecast accuracy. For a real benchmark, load a documented historical dataset (e.g., M5) and compare a lagged moving average with a time-ordered tree-model split; report MAE, RMSE, and sMAPE only where denominators permit. Avoid random train/test shuffling.

Recommended performance experiment: generate 100k, 1M, 5M and 10M event rows; time CSV generation, Spark read/transform/write, record partition count, executor configuration, output size, and peak memory. Compare only sizes that fit local memory, and state hardware/runtime. No performance numbers are fabricated in this report.

Scheduling KPIs exposed in the API include requested/scheduled/unscheduled units and completion rate. Future evaluation should additionally collect due-date lateness, utilization, changeover, shortage, objective cost, and recovery latency after failure.
