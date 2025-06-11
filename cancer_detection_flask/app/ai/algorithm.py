from app.ai.utils import load_model, load_label_encoder
import numpy as np

model = load_model()
label_encoder = load_label_encoder()


def predict(features):
    # Define the order of features the model expects
    feature_order = [
        'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean',
        'smoothness_mean', 'compactness_mean', 'concavity_mean', 'concave_points_mean',
        'symmetry_mean', 'fractal_dimension_mean', 'radius_se', 'texture_se',
        'perimeter_se', 'area_se', 'smoothness_se', 'compactness_se',
        'concavity_se', 'concave_points_se',  # add this
        'symmetry_se', 'fractal_dimension_se',
        'radius_worst', 'texture_worst', 'perimeter_worst', 'area_worst',
        'smoothness_worst', 'compactness_worst', 'concavity_worst', 'concave_points_worst',  # add this
        'symmetry_worst', 'fractal_dimension_worst'
    ]

    # Make sure 'features' is a dict with keys = feature names and values = inputs
    # or convert it into a list following the feature_order
    ordered_features = [features[name] for name in feature_order]

    # Convert to 2D array (model expects 2D)
    data = [ordered_features]

    pred_encoded = model.predict(data)[0]
    # Decode prediction as needed
    return pred_encoded

