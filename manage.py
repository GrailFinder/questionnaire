from flask_script import Manager
import unittest
import coverage
from services.questmaker import create_app, db
from services.questmaker.api.models import Question, Answer, Inquiry, User

COV = coverage.coverage(
    branch=True,
    include='services/questmaker/*',
    omit=[
        'services/questmaker/tests/*'
    ]
)

COV.start()

app = create_app()

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
    a1 = Answer("Okay")
    a2 = Answer("Good")
    a3 = Answer("Bad")
    a4 = Answer("Who are you again?")

    for a in (a1, a2, a3, a4):
        db.session.add(a)
        q1.answers.append(a)

    db.session.add(q1)
    i1.questions.append(q1)
    db.session.add(i1)


    # second question
    q1 = Question(title="Anyway how is your sex life?")
    a1 = Answer("You're just a little chicken")
    a2 = Answer("Its not true, I did not hit her. I did not")
    a3 = Answer("I am so happy to have you as my best friend and I love Lisa so much")
    a4 = Answer("If a lot of people would love each other, the world would be a better place to live")

    for a in (a1, a2, a3, a4):
        db.session.add(a)
        q1.answers.append(a)

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
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


if __name__ == '__main__':
    manager.run()