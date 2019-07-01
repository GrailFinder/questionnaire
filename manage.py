from flask_script import Manager
import unittest
import coverage
from services.questmaker import create_app, db
from services.questmaker.api.models import Question, Answer, Inquiry, User, Choice
from flask import current_app
from flask_restplus import Api

COV = coverage.coverage(
    branch=True,
    include='services/questmaker/*',
    omit=[
        'services/questmaker/tests/*'
    ]
)

COV.start()

app = create_app()
app.url_map.strict_slashes = False

manager = Manager(app)

@manager.command
def recreate_db():
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def seed_db():
    """get some data in db"""

    # user
    u0 = User(username='grail', email="test@example.com", password='test')
    db.session.add(u0)


    # first question
    i1 = Inquiry(title="Who are you from the star wars?")
    q1 = Question(title="How was your day, sweety?")
    a1 = Choice("Okay", q1.id)
    a2 = Choice("Good", q1.id)
    a3 = Choice("Bad", q1.id)
    a4 = Choice("Who are you again?", q1.id)

    for a in (a1, a2, a3, a4):
        db.session.add(a)
        q1.choices.append(a)

    db.session.add(q1)
    i1.questions.append(q1)
    db.session.add(i1)


    # second question
    q1 = Question(title="Anyway how is your sex life?")
    a1 = Choice("You're just a little chicken", q1.id)
    a2 = Choice("Its not true, I did not hit her. I did not", q1.id)
    a3 = Choice("I am so happy to have you as my best friend and I love Lisa so much", q1.id)
    a4 = Choice("If a lot of people would love each other, the world would be a better place to live", q1.id)

    for a in (a1, a2, a3, a4):
        db.session.add(a)
        q1.choices.append(a)

    db.session.add(q1)
    i1.questions.append(q1)
    u0.inquiries.append(i1)
    db.session.add(i1)

    db.session.commit()



@manager.command
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('services/questmaker/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('services/questmaker/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        current_app.logger.info('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
