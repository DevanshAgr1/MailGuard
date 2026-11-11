from flask import Blueprint, jsonify, request
from backend.services.prediction_service import PredictionService
from backend.services.database import add_prediction, recent, analytics, clear_demo
from backend.services.analytics_service import model_metrics, metadata, dataset_stats
api=Blueprint('api', __name__, url_prefix='/api')
predictor=PredictionService()
@api.get('/health')
def health(): return jsonify({'status':'online','model_loaded':True,'service':'MailGuard API'})
@api.get('/model')
def model_info(): return jsonify(metadata())
@api.get('/metrics')
def metrics(): return jsonify({'models':model_metrics(),'selected':metadata().get('best_model')})
@api.get('/analytics')
def analytics_api(): return jsonify(analytics())
@api.get('/dataset')
def dataset(): return jsonify(dataset_stats())
@api.get('/history')
def history(): return jsonify({'items':recent(int(request.args.get('limit',50)))})
@api.delete('/history/demo')
def delete_demo(): return jsonify({'deleted':clear_demo()})
@api.post('/predict')
def predict():
    body=request.get_json(silent=True) or {}; message=body.get('message','')
    try: result=predictor.predict(message)
    except ValueError as e: return jsonify({'error':str(e)}),400
    add_prediction(result,message,body.get('source','api'),0)
    return jsonify(result)
