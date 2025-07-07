"""
Machine learning engine for cancer risk prediction
"""
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from datetime import datetime


class CancerRiskPredictor:
    """Advanced ML model for cancer risk prediction."""
    
    def __init__(self, model_dir='models'):
        self.model = None
        self.scaler = None
        self.feature_names = [
            'radius_mean', 'texture_mean', 'perimeter_mean', 
            'area_mean', 'concave_points_mean', 'symmetry_mean'
        ]
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, 'cancer_model.pkl')
        self.scaler_path = os.path.join(model_dir, 'scaler.pkl')
        self.metadata_path = os.path.join(model_dir, 'model_metadata.pkl')
        self.version = '2.0'
        
        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)
        
    def load_model(self):
        """Load the trained model and scaler."""
        try:
            if self._model_files_exist():
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                # Load metadata if available
                if os.path.exists(self.metadata_path):
                    with open(self.metadata_path, 'rb') as f:
                        metadata = pickle.load(f)
                        self.version = metadata.get('version', self.version)
                
                print(f"Model v{self.version} loaded successfully")
                return True
            else:
                print("Model files not found, training new model...")
                return self.train_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            return self.train_model()
    
    def _model_files_exist(self):
        """Check if all required model files exist."""
        return (os.path.exists(self.model_path) and 
                os.path.exists(self.scaler_path))
    
    def train_model(self):
        """Train a new model with enhanced synthetic data."""
        try:
            print("Training new cancer risk prediction model...")
            
            # Generate more sophisticated synthetic training data
            X, y = self._generate_training_data()
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model with optimal parameters
            self.model = LogisticRegression(
                random_state=42, 
                max_iter=2000,
                C=1.0,
                class_weight='balanced'
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
            
            accuracy = accuracy_score(y_test, y_pred)
            auc_score = roc_auc_score(y_test, y_pred_proba)
            
            print(f"Model accuracy: {accuracy:.3f}")
            print(f"AUC score: {auc_score:.3f}")
            
            # Save model, scaler, and metadata
            self._save_model_artifacts(accuracy, auc_score)
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def _generate_training_data(self, n_samples=2000):
        """Generate realistic synthetic training data."""
        np.random.seed(42)
        
        # Enhanced data generation with more realistic distributions
        # Malignant samples (higher values, more variance)
        malignant_means = [16.5, 21.0, 110.0, 900.0, 0.09, 0.21]
        malignant_stds = [4.0, 5.0, 25.0, 250.0, 0.025, 0.04]
        
        # Benign samples (lower values, less variance)
        benign_means = [11.5, 17.0, 75.0, 500.0, 0.04, 0.17]
        benign_stds = [2.5, 3.0, 15.0, 150.0, 0.015, 0.025]
        
        # Generate malignant samples
        malignant_data = np.random.normal(
            malignant_means, malignant_stds, (n_samples//2, 6)
        )
        
        # Generate benign samples
        benign_data = np.random.normal(
            benign_means, benign_stds, (n_samples//2, 6)
        )
        
        # Ensure realistic ranges
        malignant_data = np.clip(malignant_data, 
                               [6.0, 9.0, 40.0, 140.0, 0.0, 0.1],
                               [30.0, 40.0, 200.0, 2500.0, 0.2, 0.3])
        
        benign_data = np.clip(benign_data,
                            [6.0, 9.0, 40.0, 140.0, 0.0, 0.1],
                            [30.0, 40.0, 200.0, 2500.0, 0.2, 0.3])
        
        # Combine data
        X = np.vstack([malignant_data, benign_data])
        y = np.hstack([np.ones(n_samples//2), np.zeros(n_samples//2)])
        
        # Shuffle data
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]
        
        return X, y
    
    def _save_model_artifacts(self, accuracy, auc_score):
        """Save model, scaler, and metadata."""
        # Save model
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save scaler
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save metadata
        metadata = {
            'version': self.version,
            'trained_at': datetime.utcnow().isoformat(),
            'accuracy': accuracy,
            'auc_score': auc_score,
            'feature_names': self.feature_names
        }
        
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"Model artifacts saved in {self.model_dir}/")
    
    def predict(self, features):
        """Make a prediction on new data."""
        if self.model is None or self.scaler is None:
            if not self.load_model():
                return None
        
        try:
            # Validate input
            if len(features) != 6:
                raise ValueError(f"Expected 6 features, got {len(features)}")
            
            # Convert to numpy array and reshape
            feature_array = np.array([features]).reshape(1, -1)
            
            # Scale features
            feature_scaled = self.scaler.transform(feature_array)
            
            # Make prediction
            probability = self.model.predict_proba(feature_scaled)[0][1]
            prediction = self.model.predict(feature_scaled)[0]
            
            # Determine risk level with improved thresholds
            risk_level = self._calculate_risk_level(probability)
            
            return {
                'probability': float(probability),
                'prediction': int(prediction),
                'risk_level': risk_level,
                'model_version': self.version,
                'confidence': self._calculate_confidence(probability)
            }
            
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None
    
    def _calculate_risk_level(self, probability):
        """Calculate risk level based on probability with improved thresholds."""
        if probability < 0.25:
            return "Very Low"
        elif probability < 0.45:
            return "Low"
        elif probability < 0.70:
            return "Moderate"
        else:
            return "High"
    
    def _calculate_confidence(self, probability):
        """Calculate prediction confidence."""
        # Confidence is higher when probability is closer to 0 or 1
        confidence = 2 * abs(probability - 0.5)
        return round(confidence, 3)
    
    def get_feature_importance(self):
        """Get feature importance from the model."""
        if self.model is None:
            return None
        
        if hasattr(self.model, 'coef_'):
            importance = abs(self.model.coef_[0])
            feature_importance = dict(zip(self.feature_names, importance))
            return sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        return None
    
    def validate_input(self, features):
        """Validate input features."""
        if not isinstance(features, (list, tuple, np.ndarray)):
            return False, "Features must be a list, tuple, or array"
        
        if len(features) != 6:
            return False, f"Expected 6 features, got {len(features)}"
        
        # Check ranges
        ranges = [
            (6.0, 30.0),    # radius_mean
            (9.0, 40.0),    # texture_mean
            (40.0, 200.0),  # perimeter_mean
            (140.0, 2500.0), # area_mean
            (0.0, 0.2),     # concave_points_mean
            (0.1, 0.3)      # symmetry_mean
        ]
        
        for i, (value, (min_val, max_val)) in enumerate(zip(features, ranges)):
            if not (min_val <= value <= max_val):
                return False, f"{self.feature_names[i]} must be between {min_val} and {max_val}"
        
        return True, "Valid input"


# Global model instance
cancer_predictor = CancerRiskPredictor()