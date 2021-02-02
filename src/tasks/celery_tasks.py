import os
import wikipedia

from src import celery
from src.db import get_db, close_db

import RAKE

from src import handler as db_handler


@celery.task()
def process_text(text_id):

    text = db_handler.get_item("text", text_id)

    if text:

        keywords = get_keyphrases(text)
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
                        is_exists, page_url, is_disambiguation = get_wiki_page(result)

                # sometimes full phrase isn't appear in the search results (test case "queen elizabeth ii")
                if not is_exists:
                    is_exists, page_url, is_disambiguation = get_wiki_page(phrase)

                try:
                    db_handler.create_keyphrase(text_id, phrase, page_url, is_exists, is_disambiguation)
                except TypeError:
                    print("Invalid values")


def get_keyphrases(text):
    stop_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../content/StopList.txt")
    rake_object = RAKE.Rake(stop_dir)

    keywords = rake_object.run(text.get("content", ""))
    return keywords


def get_wiki_page(phrase):
    try:
        page = wikipedia.page(phrase, auto_suggest=False, preload=False)
        page_url = page.url
        is_exists = True
        is_disambiguation = False
    except wikipedia.exceptions.DisambiguationError as error:
        is_exists = True
        is_disambiguation = True
        page_url = None
    except wikipedia.exceptions.PageError as error:
        is_exists = False
        is_disambiguation = False
        page_url = None

    return is_exists, page_url, is_disambiguation
