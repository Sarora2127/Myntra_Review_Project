# src/ml_model/utils.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import numpy as np

def preprocess_data(df: pd.DataFrame):
    # Drop rows where target (Rating_Count) is missing or invalid
    df = df.dropna(subset=["Rating_Count"])
    # Convert to numeric
    # df["Price"] = pd.to_numeric(df["Price"].str.replace("₹", ""), errors='coerce') No need
    df["Over_All_Rating"] = pd.to_numeric(df["Over_All_Rating"], errors='coerce')
    df["Rating"] = pd.to_numeric(df["Rating"], errors='coerce')
    df["Rating_Count"] = pd.to_numeric(df["Rating_Count"], errors='coerce')

    df = df.dropna(subset=["Price", "Over_All_Rating", "Rating", "Rating_Count"])
    # Basic sentiment feature engineering (no NLP, simple keyword match)
    if "Comment" in df.columns:
        df['PositiveWordCount'] = df['Comment'].str.lower().str.count(r'good|nice|amazing|awesome')
        df['NegativeWordCount'] = df['Comment'].str.lower().str.count(r'bad|poor|worst')
    else:
        df['PositiveWordCount'] = 0
        df['NegativeWordCount'] = 0

    # Dynamically check for available features
    all_possible_features = ["Price", "Over_All_Rating", "PositiveWordCount", "NegativeWordCount"] # add more in future
    existing_features = [f for f in all_possible_features if f in df.columns]
    X = df[existing_features]
    df["popularity_score"] = df["Rating"] * df["Rating_Count"]
    y = df["popularity_score"]
    # Identify numeric and categorical features dynamically
    # num_features = [f for f in ["Price", "Over_All_Rating", "Rating"] if f in existing_features]
    num_features = [f for f in existing_features if df[f].dtype in [np.float64, np.int64]]
    cat_features = list(set(existing_features) - set(num_features))

    # Preprocessing pipelines
    num_transformer = SimpleImputer(strategy='mean')
    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy='constant', fill_value='missing')),
        ("onehot", OneHotEncoder(handle_unknown='ignore'))
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_features),
            ("cat", cat_transformer, cat_features)
        ]
    )
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return preprocessor, X_train, X_test, y_train, y_test
