from services.questmaker import db
from services.questmaker.api.models import Question, Answer, Inquiry, User


def add_quest(title, multi=False):
    quest = Question(title=title, multiansw=multi)
    db.session.add(quest)
    db.session.commit()
    return quest

def add_answer(text, value=None):
    answer = Answer(text=text, value=value)
    db.session.add(answer)
    db.session.commit()
    return answer

def add_inquiry(title, description=None):
    inq = Inquiry(title=title, description=description)
    db.session.add(inq)
    db.session.commit()
    return inq

def add_user(username, email, password):
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user