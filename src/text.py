import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from src.db import get_db
from src.tasks.celery_tasks import process_text

bp = Blueprint('text', __name__, url_prefix='/text')

@bp.route('/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        text = request.form['text']

        db = get_db()
        error = None

        if not text:
            error = 'Text is required.'

        if error is None:
            cursor = db.execute(
                'INSERT INTO text (content) VALUES (?)', (text, )
            )
            db.commit()
            print("Text id is", cursor.lastrowid)
            process_text.delay(cursor.lastrowid)

            return redirect(url_for('text.create'))

        flash(error)
    texts = get_db().execute('SELECT * FROM text').fetchall()
    return render_template('text/text_list.html', texts = texts)

@bp.route('/<text_id>', methods=('GET',))
def detail(text_id):
    db = get_db()
    text = db.execute('SELECT * FROM text WHERE id=(?)', (text_id, )).fetchone()

    keyphrases = db.execute('SELECT * FROM keyphrase WHERE text_id=(?)', (text_id, )).fetchall()

    return render_template('text/text_detail.html', text=text, keyphrases=keyphrases)
