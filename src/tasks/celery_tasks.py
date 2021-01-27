import os
import wikipedia

from src import celery
from src.db import get_db

import RAKE


@celery.task()
def process_text(text_id):
    db = get_db()
    print(db.cursor())

    text = db.execute('SELECT * FROM text WHERE id=(?)', (text_id,)).fetchone()
    stop_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../content/StopList.txt")
    rake_object = RAKE.Rake(stop_dir)

    for text in db.execute('SELECT * FROM text WHERE id=(?)', (text_id,)).fetchall():
        print(text["id"])
    if text:
        keywords = rake_object.run(text["content"])

        for phrase, rank in keywords:

            if rank > 5:
                is_disambiguation = False
                is_exists = False
                page_url = None
                results = wikipedia.search(phrase, suggestion=False)
                for result in results:

                    # case sensitive wiki API
                    if result.lower() == phrase.lower():
                        try:
                            page = wikipedia.page(result, auto_suggest=False, preload=False)
                            page_url = page.url
                            is_exists = True

                        except wikipedia.exceptions.DisambiguationError as error:
                            is_exists = True
                            is_disambiguation = True
                        except wikipedia.exceptions.PageError as error:
                            pass

                db.execute("INSERT INTO keyphrase (text_id, keyphrase, wiki_url,is_exists, is_disambiguation) VALUES (?,?,?,?,?)",
                           (text_id, phrase, page_url, is_exists, is_disambiguation))
                db.commit()

