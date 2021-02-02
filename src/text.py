from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from src import handler as db_handler
from src.tasks.celery_tasks import process_text

bp = Blueprint('text', __name__, url_prefix='/text')



@bp.route('/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        text = request.form['text']

        error = None

        if not text:
            error = 'Text is required.'

        if error is None:
            last_id = db_handler.create_text(text)

            # create celery task
            process_text.delay(last_id)

            return redirect(url_for('text.create'))

        flash(error)


    texts = db_handler.get_texts()

    return render_template('text/text_list.html', texts=texts)


@bp.route('/<text_id>', methods=('GET',))
def detail(text_id):

    text = db_handler.get_item("text", text_id)

    keyphrases = db_handler.get_keyphrases_by_text(text_id)

    return render_template('text/text_detail.html', text=text, keyphrases=keyphrases)

