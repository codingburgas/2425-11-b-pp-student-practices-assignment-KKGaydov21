import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

DATA_PATH = 'app/Cancer_Data.csv'  # Adjust if your CSV is somewhere else

def main():
    df = pd.read_csv(DATA_PATH)

    # Replace 'target' with your actual label column name
    X = df.drop('target', axis=1)
    y = df['target']

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print(f"Model accuracy: {model.score(X_test, y_test):.2f}")

    # Create model directory if not exists
    model_dir = 'app/ai/model'
    os.makedirs(model_dir, exist_ok=True)

    # Save the model
    with open(os.path.join(model_dir, 'model.pkl'), 'wb') as f:
        pickle.dump(model, f)

    # Save the label encoder
    with open(os.path.join(model_dir, 'label_encoder.pkl'), 'wb') as f:
        pickle.dump(le, f)

if __name__ == '__main__':
    main()
