'''

Тестове завдання:

Написати застосунок на Python (3.8+). Можна зберегти текст, із тексту треба видобути ключові фрази (keyphrase extraction)
і також їх зберегти. Для кожної ключової фрази перевірити, чи є для них сторінка у вікіпедії (і чи вона disambiguation,
якщо є). Можна подивитись топ ключових фраз для усіх збережених текстів. Технологія фронтенду - за бажанням, можна SPA,
 можна класичні шаблони і форми без інтерактивності та джаваскріпту.

Код оформити так, як зазвичай оформляють продакшен код, викласти як відкритий репозиторій на Github/Gitlab/Bitbucket і
надіслати посилання.

Як бонус-опція, додати у репозиторій docker-compose файл, щоб однією командою можна було запустити все що потрібно.

Перевіряти буду не тільки те, чи працює, чи ні, але й наскільки просто, зрозуміло та ефективно написаний код.

'''
import os

from celery import Celery
from flask import Flask, redirect, url_for

celery = Celery(__name__, broker='redis://redis:6379')

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE="postgresql://postgres:postgres@postgresql:5432/prophy",
    )

    app.config.update(
        CELERY_BROKER_URL='redis://redis:6379'
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    celery.conf.update(app.config)

    from . import db
    db.init_app(app)

    from . import text
    app.register_blueprint(text.bp)
    app.add_url_rule('/', endpoint='index')

    @app.route("/", methods=["GET"])
    def index():
        return redirect(url_for("text.create"))

    return app

