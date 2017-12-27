from flask_testing import TestCase

from services.questmaker import create_app, db

app = create_app()

class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('services.questmaker.config.TestingConfig')
        return app

    def setUp(self):
        db.session.remove()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()