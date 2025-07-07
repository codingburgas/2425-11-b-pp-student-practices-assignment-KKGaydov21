import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


class CancerRiskModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = [
            'radius_mean', 'texture_mean', 'perimeter_mean', 
            'area_mean', 'concave_points_mean', 'symmetry_mean'
        ]
        self.model_path = 'models/cancer_model.pkl'
        self.scaler_path = 'models/scaler.pkl'
        
    def load_model(self):
        """Load the trained model and scaler"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                return True
            else:
                return self.train_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def train_model(self):
        """Train a new model with simplified features"""
        try:
            # Create synthetic training data based on medical knowledge
            # In production, you would use real medical data
            np.random.seed(42)
            n_samples = 1000
            
            # Generate realistic cancer data
            # Malignant samples (higher values)
            malignant_data = np.random.normal([15, 20, 100, 800, 0.08, 0.2], 
                                            [3, 4, 20, 200, 0.02, 0.03], 
                                            (n_samples//2, 6))
            
            # Benign samples (lower values)
            benign_data = np.random.normal([12, 17, 80, 600, 0.05, 0.18], 
                                         [2, 3, 15, 150, 0.015, 0.025], 
                                         (n_samples//2, 6))
            
            # Combine data
            X = np.vstack([malignant_data, benign_data])
            y = np.hstack([np.ones(n_samples//2), np.zeros(n_samples//2)])
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = LogisticRegression(random_state=42, max_iter=1000)
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"Model accuracy: {accuracy:.3f}")
            
            # Save model
            os.makedirs('models', exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict(self, features):
        """Make a prediction on new data"""
        if self.model is None or self.scaler is None:
            if not self.load_model():
                return None
        
        try:
            # Ensure features are in correct order
            feature_array = np.array([features]).reshape(1, -1)
            
            # Scale features
            feature_scaled = self.scaler.transform(feature_array)
            
            # Make prediction
            probability = self.model.predict_proba(feature_scaled)[0][1]
            prediction = self.model.predict(feature_scaled)[0]
            
            # Determine risk level
            if probability < 0.3:
                risk_level = "Very Low"
            elif probability < 0.5:
                risk_level = "Low"
            elif probability < 0.7:
                risk_level = "Moderate"
            else:
                risk_level = "High"
            
            return {
                'probability': float(probability),
                'prediction': int(prediction),
                'risk_level': risk_level
            }
            
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None


# Global model instance
cancer_model = CancerRiskModel()
