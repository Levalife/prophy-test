from src.db import get_db
from src.utils import parse_text, parse_keyphrase


from werkzeug.local import LocalProxy

db = LocalProxy(get_db)
tables = ("text", "keyphrase")


def get_item(table, id):
    if table in tables:
        cursor = db.cursor()
        sql_query = 'SELECT * FROM {} WHERE id=(%s)'.format(table)
        cursor.execute(sql_query, (id,))
        text = parse_text(cursor.fetchone())
        cursor.close()
        return text


def get_keyphrases_by_text(text_id):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM keyphrase WHERE text_id=(%s)', (text_id,))
    keyphrases = [parse_keyphrase(k) for k in cursor.fetchall()]
    cursor.close()
    return keyphrases


def get_texts():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM text ORDER BY id DESC')

    texts = [parse_text(t) for t in cursor.fetchall()]
    cursor.close()
    return texts


def create_text(text):
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO text (content) VALUES (%s) RETURNING id', (text,)
    )
    last_id = cursor.fetchone()[0]
    db.commit()
    cursor.close()
    return last_id


def create_keyphrase(*args):
    if isinstance(args[0], int) and isinstance(args[1], str) and \
            isinstance(args[2], (str, type(None))) and isinstance(args[3], bool) and \
            isinstance(args[4], bool):
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO keyphrase (text_id, keyphrase, wiki_url, is_exists, is_disambiguation) VALUES (%s,%s,%s,%s,%s)",
            args)
        db.commit()
        cursor.close()
    else:
        raise TypeError