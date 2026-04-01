import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
import os

# configuration
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'db', 'information_.db')
DEBUG = True

TYPE_LABELS = {1: 'Conference', 2: 'Journal', 3: 'Preprint', 4: 'Book Chapter'}
TYPE_BADGES = {1: 'C', 2: 'J', 3: 'P', 4: 'B'}

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

def _row_to_dict(row):
    return dict(id=row[0], type=row[1], title=row[2], author=row[3], confname=row[4],
                urlpaper=row[5], urlslides=row[6], urlcite=row[7], cite=row[8],
                place=row[9], year=row[10], text=row[11], video=row[12],
                urlpdf=row[14], urlaward=row[15], hidden=row[16] if len(row) > 16 else 0)

def query_entries(type_filter=None, year_filter=None, search=None, show_all=False):
    query = 'SELECT * FROM entries WHERE 1=1'
    params = []
    if not show_all:
        query += ' AND (hidden IS NULL OR hidden = 0)'
    if type_filter:
        query += ' AND type = ?'
        params.append(int(type_filter))
    if year_filter:
        query += ' AND year = ?'
        params.append(int(year_filter))
    if search:
        query += ' AND (title LIKE ? OR author LIKE ? OR confname LIKE ?)'
        term = '%{}%'.format(search)
        params.extend([term, term, term])
    query += ' ORDER BY year DESC, id ASC'
    cur = g.db.execute(query, params)
    return [_row_to_dict(row) for row in cur.fetchall()]

def query_all_entries():
    cur = g.db.execute('SELECT * FROM entries ORDER BY year DESC, id ASC')
    return [_row_to_dict(row) for row in cur.fetchall()]

@app.route("/")
def index():
    all_entries = query_all_entries()
    visible_entries = [e for e in all_entries if not e.get('hidden')]
    years = sorted(set(e['year'] for e in all_entries), reverse=True)
    types = sorted(set(e['type'] for e in all_entries))
    total_citations = sum(e['cite'] for e in all_entries)
    total_papers = len(all_entries)
    return render_template('index.html',
                           entries=visible_entries,
                           years=years,
                           types=types,
                           type_labels=TYPE_LABELS,
                           type_badges=TYPE_BADGES,
                           total_citations=total_citations,
                           total_papers=total_papers)

@app.route('/publications')
def publications():
    type_filter = request.args.get('type')
    year_filter = request.args.get('year')
    search = request.args.get('search')
    show_all = request.args.get('show_all') == '1'
    entries = query_entries(type_filter, year_filter, search, show_all)
    return render_template('_publications.html',
                           entries=entries,
                           type_badges=TYPE_BADGES,
                           show_all=show_all)

@app.route('/health')
def health():
    return 'OK', 200

@app.errorhandler(Exception)
def exception_handler(error):
    return "An error occurred: " + repr(error)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0')
