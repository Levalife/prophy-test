import pytest
import src.handler as db_handler
from src import create_app

from src.db import get_db, init_db
from src.tasks.celery_tasks import process_keyphrase


@pytest.fixture
def app():

    app = create_app({"TESTING": True, "DATABASE": "postgresql://postgres:postgres@postgresql_test:5433/prophy_test"})

    with app.app_context():
        init_db()

    yield app


@pytest.fixture
def client(app):

    return app.test_client()


def test_create_text(app):

    with app.app_context():
        id = db_handler.create_text("Some text")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM text WHERE id=(%s);", (id, ))
        text = cursor.fetchone()
        cursor.close()

    assert text is not None
    assert text[0] == id
    assert text[1] == "Some text"


def test_get_texts(app):

    with app.app_context():
        non_texts = db_handler.get_texts()

        id1 = db_handler.create_text("Some text 1")
        id2 = db_handler.create_text("Some text 2")

        texts = db_handler.get_texts()

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM text ORDER BY id DESC;")
        texts_test = cursor.fetchall()
        cursor.close()

    assert len(non_texts) == 0
    assert len(texts) == len(texts_test)
    assert texts[0].get("content") == texts_test[0][1]


def test_create_keyphrase(app):

    with app.app_context():
        id = db_handler.create_text("Some text")
        db_handler.create_keyphrase(id, "some", None, False, False)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM text WHERE id=(%s);", (id, ))
        text = cursor.fetchone()

        cursor.execute("SELECT * FROM keyphrase WHERE text_id=(%s);", (id,))
        keyphrases = cursor.fetchall()
        cursor.close()

    assert text is not None
    assert len(keyphrases) == 1
    assert keyphrases[0][1] == id
    assert keyphrases[0][2] == "some"
    assert keyphrases[0][3] == None
    assert keyphrases[0][4] == False
    assert keyphrases[0][5] == False
    assert text[1] == "Some text"


def test_get_keyphrases(app):

    with app.app_context():
        id = db_handler.create_text("Some text")
        db_handler.create_keyphrase(id, "some1", None, False, False)
        db_handler.create_keyphrase(id, "some2", None, True, True)
        db_handler.create_keyphrase(id, "some3", None, False, False)
        db_handler.create_keyphrase(id, "some4", "https://google.com", True, False)
        db_handler.create_keyphrase(id, "some5", None, False, False)

        id2 = db_handler.create_text("Some text 2")
        db_handler.create_keyphrase(id2, "some21", None, False, False)
        db_handler.create_keyphrase(id2, "some22", None, True, True)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM text WHERE id=(%s);", (id, ))
        text = cursor.fetchone()

        cursor.execute("SELECT * FROM keyphrase WHERE text_id=(%s) ORDER BY id;", (id,))
        keyphrases = cursor.fetchall()
        cursor.close()

    assert text is not None
    assert len(keyphrases) == 5
    assert keyphrases[0][1] == id
    assert keyphrases[0][2] == "some1"
    assert keyphrases[0][3] is None
    assert keyphrases[0][4] is False
    assert keyphrases[0][5] is False
    assert keyphrases[3][1] == id
    assert keyphrases[3][2] == "some4"
    assert keyphrases[3][3] == "https://google.com"
    assert keyphrases[3][4] is True
    assert keyphrases[3][5] is False

    with pytest.raises(TypeError):
        db_handler.create_keyphrase(id2, "some22", False, None, "Wrong type text")


def test_process_keyphrase():

    keyphrase1 = "google cloud"
    keyphrase2 = "queen elizabeth ii"
    keyphrase3 = "real love"
    keyphrase4 = "elephant bo-bo"

    is_exist1, page_url1, is_disambiguation1 = process_keyphrase(keyphrase1)
    is_exist2, page_url2, is_disambiguation2 = process_keyphrase(keyphrase2)
    is_exist3, page_url3, is_disambiguation3 = process_keyphrase(keyphrase3)
    is_exist4, page_url4, is_disambiguation4 = process_keyphrase(keyphrase4)

    assert is_exist1 is True
    assert page_url1 == "https://en.wikipedia.org/wiki/Google_Cloud"
    assert is_disambiguation1 == False

    assert is_exist2 is True
    assert page_url2 == "https://en.wikipedia.org/wiki/Elizabeth_II"
    assert is_disambiguation2 is False

    assert is_exist3 is True
    assert page_url3 is None
    assert is_disambiguation3 is True

    assert is_exist4 is False
    assert page_url4 is None
    assert is_disambiguation4 is False
