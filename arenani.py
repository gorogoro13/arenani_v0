# -*- coding: utf-8 -*-
"""
FlaskのURLルールはWerkzeugのルーティングモジュールに基づいている。
gオブジェクトはFlaskの特別なプロバイダー。
"""
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
import psycopg2
from contextlib import closing
from flask_sqlalchemy import SQLAlchemy

# configuration
DATABASE = 'test_nani'
DEBUG = True
SECRET_KEY = 'naninaninani'
USERNAME = 'grgr13'
PASSWORD = 'minitimati'

app = Flask(__name__)
app.config.from_object(__name__) # 大文字の変数をすべて取得
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def init_db(fname):
    """
    Need:from contextlib import closing
    Using python shell
    $ python
    $ >>> from flaskr import init_db
    $ >>> init_db('schema.sql')
    :param fname: sql-file on same directory at arenasni.py
    :return:
    """
    with closing(connect_db()) as db:
        with app.open_resource(fname, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()
    #g.db.cursor =g.db.cursor(name='are_cursor',scrollable=True,withhold=True)
@app.after_request
def after_request(response):
    """
    例外発生時などには呼び出される保証はない。通常時のみ。
    :param response:
    :return:
    """
    g.db.close()
    return response
@app.teardown_request

def teardown_request(exception):
    """
    例外発生時に実行される
    :param exception:
    :return:
    """
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def connect_db():
    con = psycopg2.connect(
        host = "localhost",
        port =5432,
        database = app.config['DATABASE'],
        user = app.config['USERNAME'],
        password = app.config['PASSWORD'])

    #print con
    return con

@app.route('/')
def show_entries():
    #print g.db
    cur = g.db.execute('select title, text from entries order by id desc')
    #cur = g.db.cursor.execute('select title, text from entries order by id desc')
    #g.db.cursor.execute.if.
    #print cur
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]

    return render_template('show_entries.html', entries=entries)

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

#def valid_login(uname, pword):
#    return log_the_user_in(request.form['username'])

#def log_the_user_in(uname):
#    hello(uname)

if __name__ == '__main__':
    app.debug = True
    app.run()
