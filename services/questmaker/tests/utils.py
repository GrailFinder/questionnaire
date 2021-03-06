from services.questmaker import db
from services.questmaker.api.models import Question, Choice, Inquiry, User, Answer


def add_quest(title, inq, multi=False):
    quest = Question(title=title, multichoice=multi)
    inq.questions.append(quest)
    db.session.add(quest)
    db.session.commit()
    return quest

def add_choice(text, quest, value=None):
    choice = Choice(text=text, value=value, question_id=quest.id)
    db.session.add(choice)
    db.session.commit()
    return choice

def add_inquiry(title, description=None, user=None):
    inq = Inquiry(title=title, description=description)
    if user:
        user.inquiries.append(inq)
    db.session.add(inq)
    db.session.commit()
    return inq

def add_user(username, email, password):
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user


def add_answer(inq_id, quest_id, choice_id, user_id=None):
    answer = Answer(inq=inq_id, question=quest_id, choice=choice_id, user=user_id)
    db.session.add(answer)
    db.session.commit()
    return answer
