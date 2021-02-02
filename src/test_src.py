import os
import tempfile

import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import src.handler as db_handler
from src import create_app

from src.db import get_db, init_db


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({"TESTING": True, "DATABASE": "postgresql://postgres:postgres@postgresql_test:5433/prophy_test"})

    # create the database and load test data
    with app.app_context():
        init_db()

    yield app

    # close and remove the temporary database
    with app.app_context():
        db = get_db()

        try:
            db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = db.cursor()
            cursor.execute("DROP DATABASE IF EXISTS prophy_test;")
            print("db dropped")
        except (Exception) as error:
            print(error)
        finally:

            if db is not None:
                db.close()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_create_text(app):

    with app.app_context():
        id = db_handler.create_text("Some text")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM text WHERE id=(%s);", (id, ))
        text = cursor.fetchone()
        cursor.close()

    assert text != None
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

    assert text != None
    assert len(keyphrases) == 1
    assert keyphrases[0][1] == id
    assert keyphrases[0][2] == "some"
    assert keyphrases[0][3] == None
    assert keyphrases[0][4] == False
    assert keyphrases[0][5] == False
    assert text[1] == "Some text"
