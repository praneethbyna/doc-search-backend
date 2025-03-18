from flask import Flask
from flask_cors import CORS
import os
from app.routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok = True)
    CORS(app)

    app.register_blueprint(api_bp, url_prefix='/api')

    return app

app = create_app()



