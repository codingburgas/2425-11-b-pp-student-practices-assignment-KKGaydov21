import pickle
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')

def load_model():
    with open(os.path.join(MODEL_DIR, 'model.pkl'), 'rb') as f:
        model = pickle.load(f)
    return model

def load_label_encoder():
    with open(os.path.join(MODEL_DIR, 'label_encoder.pkl'), 'rb') as f:
        le = pickle.load(f)
    return le
