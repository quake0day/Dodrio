import sqlite3
import os
from flask import Flask, g, render_template, request, jsonify

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'db', 'information_.db')

app = Flask(__name__, static_folder='../static')
app.config['DATABASE'] = DATABASE

TYPE_LABELS = {1: 'Conference', 2: 'Journal', 3: 'Preprint', 4: 'Book Chapter'}
TYPE_BADGES = {1: 'C', 2: 'J', 3: 'P', 4: 'B'}


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def query_entries(type_filter=None, year_filter=None, search=None, show_all=False):
    db = get_db()
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
        term = f'%{search}%'
        params.extend([term, term, term])
    query += ' ORDER BY year DESC, id ASC'
    return db.execute(query, params).fetchall()


@app.route('/')
def index():
    db = get_db()
    all_entries = db.execute('SELECT * FROM entries ORDER BY year DESC, id ASC').fetchall()
    visible_entries = [e for e in all_entries if not e['hidden']]
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
    """htmx endpoint: returns filtered publication list as HTML fragment."""
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
