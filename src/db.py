import os
import sqlite3
from urllib import parse

import click
import psycopg2
from flask import current_app, g
from flask.cli import with_appcontext


# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row
#
#     return g.db

def connect_db():
    parse.uses_netloc.append("postgres")
    if "DATABASE_URL" in os.environ:
        url = parse.urlparse(os.environ["DATABASE_URL"])
    else:
        url = parse.urlparse(current_app.config["DATABASE"])
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
        )
    print("***OPENING CONNECTION***")
    return conn

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db.cursor()



def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    # with current_app.open_resource('schema.sql') as f:
    #     db.executescript(f.read().decode('utf8'))

    command = '''
        DROP TABLE IF EXISTS text;
        DROP TABLE IF EXISTS keyphrase;
        
        CREATE TABLE text (
          id SERIAL PRIMARY KEY,
          content VARCHAR(10000) NOT NULL
        );
        
        CREATE TABLE keyphrase (
          id SERIAL PRIMARY KEY,
          text_id INTEGER NOT NULL,
          keyphrase VARCHAR(64) NOT NULL,
          wiki_url VARCHAR(64) NULL,
          is_exists BOOLEAN NULL,
          is_disambiguation BOOLEAN NULL,
          FOREIGN KEY (text_id) REFERENCES text (id)
        );
        SELECT * FROM pg_catalog.pg_tables;
        SELECT * from text;
    '''
    try:
        db.execute(command)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        print("success")
        if db is not None:
            db.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)