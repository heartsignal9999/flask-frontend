# routes.py
from flask import Flask
from app.routes import main, index, upload_file

def create_app():
    app = Flask(__name__, static_folder='static')
    register_routes(app)
    return app

def register_routes(app):
    app.add_url_rule('/', 'main', main)
    app.add_url_rule('/index', 'index', index)
    app.add_url_rule('/upload', 'upload_file', upload_file, methods=['POST'])

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)