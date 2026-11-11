from app import app

def test_health():
    c=app.test_client(); r=c.get('/api/health'); assert r.status_code==200; assert r.json['model_loaded']
def test_predict():
    c=app.test_client(); r=c.post('/api/predict',json={'message':'Congratulations! Claim your free prize now at http://example.com'}); assert r.status_code==200; assert 'confidence' in r.json

def test_empty():
    c=app.test_client(); assert c.post('/api/predict',json={'message':''}).status_code==400
