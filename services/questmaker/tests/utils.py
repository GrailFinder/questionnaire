from services.questmaker import db
from services.questmaker.api.models import Question


def add_quest(title, multi=False):
    quest = Question(title=title, multiansw=multi)
    db.session.add(quest)
    db.session.commit()
    return quest