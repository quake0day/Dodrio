import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from wcg import init, getBadges, getRanks
import os

# configuration
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'db', 'information_.db')
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't'] 


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    cur = g.db.execute('select * from entries order by year desc')
    entries = [dict(id=row[0], type=row[1], title=row[2], author=row[3], confname=row[4], urlpaper=row[5], urlslides=row[6], urlcite=row[7], cite=row[8], place=row[9], year=row[10], text=row[11], video=row[12], urlpdf=row[14]) for row in cur.fetchall()]
   
    res = []
    return render_template('index.html', entries=entries, badges = res)

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return 'OK', 200

@app.errorhandler(Exception)
def exception_handler(error):
    app.logger.error(f'An error occurred: {error}')
    return f"An error occurred: {repr(error)}", 500

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
