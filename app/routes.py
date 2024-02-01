# app/routes.py
from flask import render_template
from .uploader import upload_file

def main():
    return render_template('intro.html')

def index():
    return render_template('index.html')
    
def configure_routes(app):
    app.add_url_rule('/', 'main', main)
    app.add_url_rule('/index', 'index', index)
    app.add_url_rule('/upload', 'upload_file', upload_file, methods=['POST'])
