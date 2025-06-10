from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SurveyForm(FlaskForm):
    # Replace these with your actual dataset feature names and types
    feature1 = FloatField('Feature 1', validators=[DataRequired(), NumberRange(min=0)])
    feature2 = FloatField('Feature 2', validators=[DataRequired(), NumberRange(min=0)])
    feature3 = FloatField('Feature 3', validators=[DataRequired(), NumberRange(min=0)])
    # Add more features as necessary

    submit = SubmitField('Predict')

    def feature_fields(self):
        # Returns list of field names for iteration in template
        return [field.name for field in self if field.name != 'submit' and field.name != 'csrf_token']
