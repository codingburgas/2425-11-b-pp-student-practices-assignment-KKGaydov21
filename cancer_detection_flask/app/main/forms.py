from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired

class SurveyForm(FlaskForm):
    radius_mean = FloatField('Radius Mean', validators=[DataRequired()])
    texture_mean = FloatField('Texture Mean', validators=[DataRequired()])
    perimeter_mean = FloatField('Perimeter Mean', validators=[DataRequired()])
    area_mean = FloatField('Area Mean', validators=[DataRequired()])
    smoothness_mean = FloatField('Smoothness Mean', validators=[DataRequired()])
    compactness_mean = FloatField('Compactness Mean', validators=[DataRequired()])
    concavity_mean = FloatField('Concavity Mean', validators=[DataRequired()])
    concave_points_mean = FloatField('Concave Points Mean', validators=[DataRequired()])
    symmetry_mean = FloatField('Symmetry Mean', validators=[DataRequired()])
    fractal_dimension_mean = FloatField('Fractal Dimension Mean', validators=[DataRequired()])
    radius_se = FloatField('Radius SE', validators=[DataRequired()])
    texture_se = FloatField('Texture SE', validators=[DataRequired()])
    perimeter_se = FloatField('Perimeter SE', validators=[DataRequired()])
    area_se = FloatField('Area SE', validators=[DataRequired()])
    smoothness_se = FloatField('Smoothness SE', validators=[DataRequired()])
    compactness_se = FloatField('Compactness SE', validators=[DataRequired()])
    concavity_se = FloatField('Concavity SE', validators=[DataRequired()])
    concave_points_se = FloatField('Concave Points SE', validators=[DataRequired()])
    symmetry_se = FloatField('Symmetry SE', validators=[DataRequired()])
    fractal_dimension_se = FloatField('Fractal Dimension SE', validators=[DataRequired()])
    radius_worst = FloatField('Radius Worst', validators=[DataRequired()])
    texture_worst = FloatField('Texture Worst', validators=[DataRequired()])
    perimeter_worst = FloatField('Perimeter Worst', validators=[DataRequired()])
    area_worst = FloatField('Area Worst', validators=[DataRequired()])
    smoothness_worst = FloatField('Smoothness Worst', validators=[DataRequired()])
    compactness_worst = FloatField('Compactness Worst', validators=[DataRequired()])
    concavity_worst = FloatField('Concavity Worst', validators=[DataRequired()])
    concave_points_worst = FloatField('Concave Points Worst', validators=[DataRequired()])
    symmetry_worst = FloatField('Symmetry Worst', validators=[DataRequired()])
    fractal_dimension_worst = FloatField('Fractal Dimension Worst', validators=[DataRequired()])

    submit = SubmitField('Predict')

    def feature_fields(self):
        return [field.name for field in self if isinstance(field, FloatField)]

