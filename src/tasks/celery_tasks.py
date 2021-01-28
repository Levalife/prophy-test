import os
import wikipedia

from src import celery
from src.db import get_db, close_db

import RAKE


@celery.task()
def process_text(text_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM text WHERE id=(%s)', (text_id,))
    text = cursor.fetchone()

    stop_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../content/StopList.txt")
    rake_object = RAKE.Rake(stop_dir)

    if text:
        keywords = rake_object.run(text[1])

        for phrase, rank in keywords:

            if rank > 5:
                is_disambiguation = False
                is_exists = False
                page_url = None
                results = wikipedia.search(phrase, suggestion=False)
                for result in results:

                    # case sensitive wiki API + API may return higher ranked but not precise page
                    # (test cases "google cloud", "Google Cloud" vs "Google Cloud Platform")
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

                # sometimes full phrase isn't appear in the search results (test case "queen elizabeth ii")
                if not is_exists:
                    try:
                        page = wikipedia.page(phrase, auto_suggest=False, preload=False)
                        page_url = page.url
                        is_exists = True
                    except wikipedia.exceptions.DisambiguationError as error:
                        pass
                    except wikipedia.exceptions.PageError as error:
                        pass

                cursor.execute("INSERT INTO keyphrase (text_id, keyphrase, wiki_url,is_exists, is_disambiguation) VALUES (%s,%s,%s,%s,%s)",
                           (text_id, phrase, page_url, is_exists, is_disambiguation))
                db.commit()
    close_db()
