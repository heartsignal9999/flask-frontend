# main.py
from flask import Flask
from app.routes import configure_routes

def create_app():
    app = Flask(__name__, static_folder='static')
    configure_routes(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)