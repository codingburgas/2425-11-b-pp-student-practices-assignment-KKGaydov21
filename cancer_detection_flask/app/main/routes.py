
from ..ai.algorithm import predict
from flask_login import login_required, current_user
from .forms import SurveyForm
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('main/index.html')


@bp.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    form = SurveyForm()
    if form.validate_on_submit():
        # Create a dict of feature_name: value pairs, excluding submit and csrf_token
        features = {field.name: field.data for field in form if field.name not in ['submit', 'csrf_token']}

        prediction = predict(features)
        return render_template('main/prediction.html', prediction=prediction)
    return render_template('main/survey.html', form=form)
