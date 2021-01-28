
import psycopg2
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from src.db import get_db, close_db
from src.tasks.celery_tasks import process_text
from src.utils import parse_text, parse_keyphrase

bp = Blueprint('text', __name__, url_prefix='/text')

@bp.route('/', methods=('GET', 'POST'))
def create():
    db = get_db()
    if request.method == 'POST':
        text = request.form['text']


        error = None

        if not text:
            error = 'Text is required.'

        if error is None:
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO text (content) VALUES (%s) RETURNING id', (text,)
            )
            last_id = cursor.fetchone()[0]
            db.commit()

            process_text.delay(last_id)

            cursor.close()
            close_db()
            return redirect(url_for('text.create'))

        flash(error)

    cursor = db.cursor()
    cursor.execute('SELECT * FROM text ORDER BY id DESC')

    texts = [parse_text(t) for t in cursor.fetchall()]

    cursor.close()
    close_db()
    return render_template('text/text_list.html', texts=texts)


@bp.route('/<text_id>', methods=('GET',))
def detail(text_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM text WHERE id=(%s)', (text_id, ))
    text = parse_text(cursor.fetchone())

    cursor.execute('SELECT * FROM keyphrase WHERE text_id=(%s)', (text_id, ))
    keyphrases = [parse_keyphrase(k) for k in cursor.fetchall()]

    cursor.close()
    close_db()
    return render_template('text/text_detail.html', text=text, keyphrases=keyphrases)

