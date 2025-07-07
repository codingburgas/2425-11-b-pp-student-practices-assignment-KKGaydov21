import os
from dotenv import load_dotenv

print("Loading .env file...")
load_dotenv()

print("Environment variables loaded:")
for k, v in os.environ.items():
    if "DATABASE" in k:
        print(f"{k}={v}")

DATABASE_URL = os.getenv('DATABASE_URL')
print("DATABASE_URL value:", DATABASE_URL)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not found")

import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd

# Database configuration with connection pooling
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not found")

from sqlalchemy import pool
engine = create_engine(
    DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Mean measurements
    radius_mean = Column(Float)
    texture_mean = Column(Float)
    perimeter_mean = Column(Float)
    area_mean = Column(Float)
    smoothness_mean = Column(Float)
    compactness_mean = Column(Float)
    concavity_mean = Column(Float)
    concave_points_mean = Column(Float)
    symmetry_mean = Column(Float)
    fractal_dimension_mean = Column(Float)
    
    # Standard error measurements
    radius_se = Column(Float)
    texture_se = Column(Float)
    perimeter_se = Column(Float)
    area_se = Column(Float)
    smoothness_se = Column(Float)
    compactness_se = Column(Float)
    concavity_se = Column(Float)
    concave_points_se = Column(Float)
    symmetry_se = Column(Float)
    fractal_dimension_se = Column(Float)
    
    # Worst measurements
    radius_worst = Column(Float)
    texture_worst = Column(Float)
    perimeter_worst = Column(Float)
    area_worst = Column(Float)
    smoothness_worst = Column(Float)
    compactness_worst = Column(Float)
    concavity_worst = Column(Float)
    concave_points_worst = Column(Float)
    symmetry_worst = Column(Float)
    fractal_dimension_worst = Column(Float)
    
    # Prediction results
    prediction_probability = Column(Float)
    prediction_class = Column(Integer)  # 0 = benign, 1 = malignant
    risk_level = Column(String(20))
    
    # Optional user information
    user_id = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    full_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_assessment = Column(DateTime, nullable=True)
    total_assessments = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_survey_response(survey_data, prediction_result, user_id=None):
    """Save survey response to database"""
    db = SessionLocal()
    try:
        # Create new survey response
        response = SurveyResponse(
            # Mean values
            radius_mean=survey_data[0],
            texture_mean=survey_data[1],
            perimeter_mean=survey_data[2],
            area_mean=survey_data[3],
            smoothness_mean=survey_data[4],
            compactness_mean=survey_data[5],
            concavity_mean=survey_data[6],
            concave_points_mean=survey_data[7],
            symmetry_mean=survey_data[8],
            fractal_dimension_mean=survey_data[9],
            
            # Standard error values
            radius_se=survey_data[10],
            texture_se=survey_data[11],
            perimeter_se=survey_data[12],
            area_se=survey_data[13],
            smoothness_se=survey_data[14],
            compactness_se=survey_data[15],
            concavity_se=survey_data[16],
            concave_points_se=survey_data[17],
            symmetry_se=survey_data[18],
            fractal_dimension_se=survey_data[19],
            
            # Worst values
            radius_worst=survey_data[20],
            texture_worst=survey_data[21],
            perimeter_worst=survey_data[22],
            area_worst=survey_data[23],
            smoothness_worst=survey_data[24],
            compactness_worst=survey_data[25],
            concavity_worst=survey_data[26],
            concave_points_worst=survey_data[27],
            symmetry_worst=survey_data[28],
            fractal_dimension_worst=survey_data[29],
            
            # Prediction results
            prediction_probability=prediction_result['probability'],
            prediction_class=prediction_result['prediction'],
            risk_level=prediction_result['risk_level'],
            user_id=user_id
        )
        
        db.add(response)
        db.commit()
        db.refresh(response)
        
        # Update user statistics if user_id provided
        if user_id:
            update_user_stats(db, user_id)
        
        return response.id
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def update_user_stats(db, user_id):
    """Update user statistics"""
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user:
        user.last_assessment = datetime.utcnow()
        user.total_assessments += 1
    else:
        user = User(
            user_id=user_id,
            last_assessment=datetime.utcnow(),
            total_assessments=1
        )
        db.add(user)
    
    db.commit()

def get_user_history(user_id, limit=10):
    """Get user's assessment history"""
    db = SessionLocal()
    try:
        responses = db.query(SurveyResponse).filter(
            SurveyResponse.user_id == user_id
        ).order_by(
            SurveyResponse.timestamp.desc()
        ).limit(limit).all()
        
        return responses
    except Exception as e:
        print(f"Database error in get_user_history: {e}")
        db.rollback()
        return []
    finally:
        db.close()

def get_assessment_statistics():
    """Get overall assessment statistics"""
    db = SessionLocal()
    try:
        total_assessments = db.query(SurveyResponse).count()
        malignant_count = db.query(SurveyResponse).filter(
            SurveyResponse.prediction_class == 1
        ).count()
        benign_count = total_assessments - malignant_count
        
        avg_probability = db.query(sa.func.avg(SurveyResponse.prediction_probability)).scalar()
        
        # Risk level distribution
        risk_distribution = db.query(
            SurveyResponse.risk_level,
            sa.func.count(SurveyResponse.risk_level)
        ).group_by(SurveyResponse.risk_level).all()
        
        return {
            'total_assessments': total_assessments,
            'malignant_count': malignant_count,
            'benign_count': benign_count,
            'average_risk': float(avg_probability) if avg_probability else 0,
            'risk_distribution': {level: count for level, count in risk_distribution}
        }
    except Exception as e:
        print(f"Database error in get_assessment_statistics: {e}")
        return {
            'total_assessments': 0,
            'malignant_count': 0,
            'benign_count': 0,
            'average_risk': 0,
            'risk_distribution': {}
        }
    finally:
        db.close()

def export_survey_data():
    """Export all survey data to DataFrame"""
    db = SessionLocal()
    try:
        query = db.query(SurveyResponse)
        df = pd.read_sql(query.statement, db.bind)
        return df
    finally:
        db.close()

def get_recent_assessments(limit=50):
    """Get recent assessments for monitoring"""
    db = SessionLocal()
    try:
        responses = db.query(SurveyResponse).order_by(
            SurveyResponse.timestamp.desc()
        ).limit(limit).all()
        
        return responses
    finally:
        db.close()