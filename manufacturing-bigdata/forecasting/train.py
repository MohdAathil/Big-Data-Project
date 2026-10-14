"""Train and compare forecasting models from daily demand CSV data.

Input columns: date, product_id, demand. Split is chronological, never shuffled.
"""
import argparse
import json
from pathlib import Path


def add_features(df):
    import pandas as pd
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['product_id', 'date'])
    grouped = df.groupby('product_id')['demand']
    for lag in (1, 7, 14, 28):
        df[f'lag_{lag}'] = grouped.shift(lag)
    for win in (7, 14, 28):
        df[f'rolling_mean_{win}'] = grouped.transform(lambda s: s.shift(1).rolling(win, min_periods=1).mean())
    df['rolling_std_7'] = grouped.transform(lambda s: s.shift(1).rolling(7, min_periods=2).std())
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['trend'] = (df['date'] - df['date'].min()).dt.days
    df['product_code'] = df['product_id'].astype('category').cat.codes
    return df.dropna(subset=['lag_1', 'lag_7']).fillna(0)


def metrics(actual, predicted):
    import numpy as np
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    mae = float(np.mean(np.abs(actual - predicted)))
    rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
    denom = np.abs(actual) + np.abs(predicted)
    smape = float(np.mean(np.divide(2 * np.abs(actual - predicted), denom, out=np.zeros_like(denom), where=denom != 0)) * 100)
    return {'mae': round(mae, 4), 'rmse': round(rmse, 4), 'smape_pct': round(smape, 4)}


def train(input_csv, output_json, train_fraction=.8):
    import pandas as pd
    from sklearn.ensemble import HistGradientBoostingRegressor
    raw = pd.read_csv(input_csv)
    needed = {'date', 'product_id', 'demand'}
    if not needed.issubset(raw.columns):
        raise ValueError(f'Input must contain {sorted(needed)}')
    data = add_features(raw)
    dates = sorted(data['date'].unique())
    if len(dates) < 3:
        raise ValueError('Need at least three dates after lag feature generation')
    split = max(1, min(len(dates)-1, int(len(dates) * train_fraction)))
    cutoff = dates[split]
    train_df, test_df = data[data.date < cutoff], data[data.date >= cutoff]
    if train_df.empty or test_df.empty:
        raise ValueError('Chronological split produced an empty train or test set')
    feature_cols = [c for c in data.columns if c.startswith(('lag_', 'rolling_'))] + ['day_of_week', 'month', 'trend', 'product_code']
    baseline = test_df['lag_7'].fillna(test_df['lag_1']).to_numpy()
    model = HistGradientBoostingRegressor(max_iter=120, learning_rate=.08, max_leaf_nodes=15, l2_regularization=1.0, random_state=17)
    model.fit(train_df[feature_cols], train_df['demand'])
    pred = model.predict(test_df[feature_cols]).clip(min=0)
    result = {'model':'HistGradientBoostingRegressor', 'train_rows':len(train_df), 'test_rows':len(test_df), 'train_end':str(train_df.date.max().date()), 'test_start':str(test_df.date.min().date()), 'baseline_metrics':metrics(test_df['demand'],baseline), 'model_metrics':metrics(test_df['demand'],pred), 'feature_columns':feature_cols}
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--output',default='data/curated/model_metrics.json'); a=p.parse_args()
    print(json.dumps(train(a.input,a.output),indent=2))
