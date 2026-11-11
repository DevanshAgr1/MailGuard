from flask import Flask, render_template
from flask_cors import CORS
from backend.api.routes import api
from backend.services.database import init_db, seed_demo
BASE=None
app=Flask(__name__, template_folder='dashboard/templates', static_folder='dashboard/static')
CORS(app, resources={r'/api/*': {'origins': '*'}})
app.register_blueprint(api)
init_db(); seed_demo()
@app.route('/')
def dashboard(): return render_template('dashboard.html')
@app.route('/detector')
def detector(): return render_template('dashboard.html', initial_page='detector')
if __name__=='__main__': app.run(host='127.0.0.1', port=5000, debug=True)
