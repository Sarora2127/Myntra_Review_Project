# src/ml_model/train_model.py
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
from src.ml_model.utils import preprocess_data

def train_models(df: pd.DataFrame):
    preprocessor, X_train, X_test, y_train, y_test = preprocess_data(df) # <-- error here 
    results = []
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
    }

    for name, model in models.items():
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model)
        ])

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        # rmse = root_mean_squared_error(y_test, y_pred, squared=False)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        # Feature importance
        if hasattr(model, "feature_importances_"):
            try:
                feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()
                importances = model.feature_importances_
                feature_importance_df = pd.DataFrame({
                    "Feature": feature_names,
                    "Importance": importances
                }).sort_values(by="Importance", ascending=False)
            except Exception as e:
                print(f"Feature importance extraction failed for {name}: {e}")
                feature_importance_df = None
        else:
            feature_importance_df = None

        results.append({
            "name": name,
            "model": model,
            "rmse": rmse,
            "r2": r2,
            "feature_importance": feature_importance_df
        })
    return results
