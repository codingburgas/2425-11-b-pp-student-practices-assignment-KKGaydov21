from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from ..main import bp
from ..main.forms import SurveyForm
from ..ai.algorithm import predict

@bp.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    form = SurveyForm()
    if form.validate_on_submit():
        features = {field.name: field.data for field in form if field.name != 'submit' and field.name != 'csrf_token'}
        prediction = predict(features)
        return render_template('main/prediction.html', prediction=prediction)
    return render_template('main/survey.html', form=form)

@bp.route('/')
def index():
    return render_template('main/index.html')
