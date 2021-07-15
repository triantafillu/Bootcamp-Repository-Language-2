import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from tensorflow import keras

from .preprocessing import preprocess_input

import pandas as pd

bp = Blueprint('auth', __name__, url_prefix='/predict')

THEMES_TO_PREDICT = ['nature', 'family', 'love', 'body', 'animals', 'arts & sciences', 'religion', 'death', 'war', 'history & politics', 'heartache']

@bp.route('', methods=('GET', 'POST'))
def predict():
    if request.method == 'POST':
        #return str(request.form)
        title = request.form['poem-title']
        text = request.form['poem-text']
        error = None
      

        if len(title + text) < 150:
            error = 'The text is too short.'

        if error is None:
            #here we use our models to predict
            predictions = {}
            df_input = pd.DataFrame([[title, text]], columns=['title', 'text'])
            df_preproc = preprocess_input(df_input)
            predictions['themes'] =  predict_categories(df_preproc)
            predictions['year'] =  predict_year(df_preproc)
            
            return render_template('prediction_result.html', predictions=predictions)

        flash(error)

    return render_template('predict.html')


def load_models():
    
    bin_models = {}
    for theme in THEMES_TO_PREDICT:
        bin_models['model_' + theme] = keras.models.load_model('flask-app/baby_models/model_' + theme + '.h5')
        
    return bin_models


def predict_categories(df_input_prp):
    bin_models = load_models()
    
    models_predictions = {}
    for theme in THEMES_TO_PREDICT:
        bin_mod = bin_models['model_' + theme]

        predictions = bin_mod.predict(df_input_prp)
        models_predictions['model_' + theme] = predictions[0][0]
    
    models_predictions = normalize_preds(models_predictions)
    
    return models_predictions
    

def normalize_preds(models_predictions):
    norm_coef = 1/sum(models_predictions.values())
    for key, value in models_predictions.items():
        models_predictions[key] = models_predictions[key]*norm_coef
    
    return models_predictions

    
def predict_year(df_input_prp):
    year_prediction_model = keras.models.load_model('flask-app/year_prediction_model.h5', compile=False)
    year_prediction = round(year_prediction_model.predict([df_input_prp])[0][0])
        
    return year_prediction
