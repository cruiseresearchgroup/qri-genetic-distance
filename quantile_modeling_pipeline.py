import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

np.random.seed(42)

df = pd.read_csv("input_data.csv")

df = df.dropna(subset=['k80', 'delta_days', 'family1', 'family2', 'state_distance_km', 'year'])
df['delta_days'] = df['delta_days'].astype(float)
df['k80'] = df['k80'].astype(float)
df['year'] = df['year'].astype(int)

quantiles = df['k80'].quantile([0, 0.33, 0.66, 1.0]).values
df['divergence_class'] = pd.cut(df['k80'], bins=quantiles,
                                labels=['low', 'mid', 'high'], include_lowest=True)

df['same_family'] = (df['family1'] == df['family2']).astype(int)
df['same_state'] = (df['state1'] == df['state2']).astype(int)
df['interaction_term'] = df['delta_days'] * df['state_distance_km']

all_features = ['delta_days', 'family1', 'family2', 'state_distance_km',
                'same_family', 'same_state', 'interaction_term', 'year']

def train_quantile_models(df_sub, label, drop_features=None):
    if drop_features is None:
        drop_features = []

    selected_features = [f for f in all_features if f not in drop_features]
    X = df_sub[selected_features]
    y = df_sub['k80']

    cat_features = [f for f in selected_features if f in ['family1', 'family2']]
    num_features = [f for f in selected_features if f not in cat_features]

    preprocessor = ColumnTransformer([
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features),
        ('num', StandardScaler(), num_features)
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        'lower': Pipeline([('pre', preprocessor), ('gbr', GradientBoostingRegressor(loss='quantile', alpha=0.05, random_state=42))]),
        'median': Pipeline([('pre', preprocessor), ('gbr', GradientBoostingRegressor(loss='quantile', alpha=0.5, random_state=42))]),
        'upper': Pipeline([('pre', preprocessor), ('gbr', GradientBoostingRegressor(loss='quantile', alpha=0.95, random_state=42))])
    }

    for m in models.values():
        m.fit(X_train, y_train)

    preds = {
        'true_k80': y_test,
        'predicted_5%': models['lower'].predict(X_test),
        'predicted_50%': models['median'].predict(X_test),
        'predicted_95%': models['upper'].predict(X_test),
    }

    results = pd.DataFrame(preds)
    results['class'] = label
    results['residual'] = results['true_k80'] - results['predicted_50%']

    print(f"\n--- {label.upper()} CLASS ({', '.join(drop_features) if drop_features else 'Full model'}) ---")
    print(results.describe())

    def compute_metrics(y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_true - y_pred) / np.clip(np.abs(y_true), 1e-8, None)))
        r2 = r2_score(y_true, y_pred)
        return {'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'MAPE': mape, 'R2': r2}

    metrics = {
        '5% Quantile': compute_metrics(y_test, results['predicted_5%']),
        '50% Quantile': compute_metrics(y_test, results['predicted_50%']),
        '95% Quantile': compute_metrics(y_test, results['predicted_95%']),
        'Coverage (90%)': np.mean((y_test >= results['predicted_5%']) & (y_test <= results['predicted_95%']))
    }

    print(f"\nValidation Metrics for {label.upper()} class:")
    for key, val in metrics.items():
        if isinstance(val, dict):
            print(f"  {key}:")
            for m, v in val.items():
                print(f"    {m}: {v:.6f}")
        else:
            print(f"  {key}: {val:.3%}")

    return results

if __name__ == "__main__":
    ablation_results = []
    for label in ['low', 'mid', 'high']:
        subset = df[df['divergence_class'] == label].copy()
        if not subset.empty:
            ablation_results.append(train_quantile_models(subset, label))
            for f in all_features:
                ablation_results.append(train_quantile_models(subset, label, drop_features=[f]))

    all_ablation_df = pd.concat(ablation_results, ignore_index=True)
    print("\nFull prediction results preview:")
    print(all_ablation_df.head())
    print(all_ablation_df.describe())
    all_ablation_df.to_csv("output_ablation_results.csv", index=False)
