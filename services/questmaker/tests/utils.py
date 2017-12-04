from services.questmaker import db
from services.questmaker.api.models import Question, Answer


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