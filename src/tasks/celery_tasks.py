import os
import re

import nltk
import wikipedia
import RAKE

from src import celery
from src import handler as db_handler

min_rank = 0
stop_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../content/StopList.txt")
rake_object = RAKE.Rake(stop_dir)

cleanr1 = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6})|\[[0-9]*\]')
cleanr2 = re.compile('\\r\\n')

lemmatizer = nltk.WordNetLemmatizer()

@celery.task()
def process_text(text_id):

    text = db_handler.get_item("text", text_id)
    if text:
        keywords = get_keyphrases(text)
        for phrase, rank in keywords:
            if rank > min_rank:
                try:
                    is_exists, page_url, is_disambiguation = process_keyphrase(phrase)

                    try:
                        db_handler.create_keyphrase(text_id, phrase, page_url, is_exists, is_disambiguation)
                    except TypeError:
                        pass
                except wikipedia.exceptions.WikipediaException:
                    pass


def get_keyphrases(text):

    keywords = rake_object.run(lemmatize_text(clean_text(text.get("content", ""))))
    return keywords


def clean_text(raw_text):

    cleantext = re.sub(cleanr1, '', raw_text)
    cleantext = re.sub(cleanr2, ' ', cleantext)
    return cleantext


def lemmatize_text(text):

    words = nltk.word_tokenize(text)
    return " ".join([lemmatizer.lemmatize(word.lower()) for word in words])


def process_keyphrase(phrase):

    results = wikipedia.search(phrase, suggestion=False)
    for result in results:

        # case sensitive wiki API + API may return higher ranked but not precise page
        # (test cases "google cloud", "Google Cloud" vs "Google Cloud Platform")
        if result.lower() == phrase:
            return get_wiki_page(result)

    # sometimes full phrase isn't appear in the search results (test case "queen elizabeth ii")
    return get_wiki_page(phrase)


def get_wiki_page(phrase):

    is_exists = True
    is_disambiguation = False
    page_url = None

    try:
        page = wikipedia.page(phrase, auto_suggest=False, preload=False, redirect=True)
        page_url = page.url
    except wikipedia.exceptions.DisambiguationError:
        is_disambiguation = True
    except wikipedia.exceptions.PageError:
        is_exists = False

    return is_exists, page_url, is_disambiguation
