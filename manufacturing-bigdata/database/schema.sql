CREATE TABLE IF NOT EXISTS products (product_id TEXT PRIMARY KEY, product_name TEXT NOT NULL, category TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS machines (machine_id TEXT PRIMARY KEY, machine_type TEXT NOT NULL, current_status TEXT NOT NULL DEFAULT 'AVAILABLE');
CREATE TABLE IF NOT EXISTS inventory (product_id TEXT REFERENCES products(product_id), warehouse_id TEXT, current_stock INTEGER NOT NULL, safety_stock INTEGER NOT NULL, incoming_quantity INTEGER NOT NULL DEFAULT 0, reserved_quantity INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(product_id, warehouse_id));
CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, customer_id TEXT, product_id TEXT REFERENCES products(product_id), quantity INTEGER, priority TEXT, promised_date DATE, status TEXT);
CREATE TABLE IF NOT EXISTS forecasts (product_id TEXT, forecast_date DATE, baseline_units NUMERIC, adjusted_units NUMERIC, model_version TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS news_events (event_id BIGSERIAL PRIMARY KEY, event_type TEXT, payload JSONB, source_url TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS schedules (job_id TEXT PRIMARY KEY, machine_id TEXT, product_id TEXT, quantity INTEGER, start_time TIMESTAMPTZ, end_time TIMESTAMPTZ, status TEXT);
