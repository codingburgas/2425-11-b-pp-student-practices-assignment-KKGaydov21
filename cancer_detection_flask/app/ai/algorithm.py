from app.ai.utils import load_model, load_label_encoder
import numpy as np

model = load_model()
label_encoder = load_label_encoder()


def predict(features: dict) -> str:
    # Extract features in correct order and convert to array
    # Assuming feature keys are consistent with training data column names
    feature_order = sorted(features.keys())  # Or use a fixed list matching training data
    data = np.array([features[key] for key in feature_order]).reshape(1, -1)

    pred_encoded = model.predict(data)[0]
    pred_label = label_encoder.inverse_transform([pred_encoded])[0]
    return pred_label
