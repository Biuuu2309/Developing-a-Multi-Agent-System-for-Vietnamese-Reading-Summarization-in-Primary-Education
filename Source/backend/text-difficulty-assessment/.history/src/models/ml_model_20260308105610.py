# src/models/ml_model.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


class MLModel:

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

    def train(self, df, feature_columns, target_column="grade"):

        X = df[feature_columns]
        y = df[target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42
        )

        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)

        acc = accuracy_score(y_test, preds)

        print("Model accuracy:", acc)

    def predict(self, features):

        df = pd.DataFrame([features])

        return self.model.predict(df)[0]
