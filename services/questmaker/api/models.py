from services.questmaker import db
import datetime, uuid

class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.String(128), nullable=False, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    multiansw = db.Column(db.Boolean)

    def __init__(self, title, multiansw=False, created_at=datetime.datetime.now()):
        self.id = str(uuid.uuid1())
        self.title = title
        self.created_at = created_at
        self.multiansw = multiansw

class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.String(128), nullable=False, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    value = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, text, value=None, created_at=datetime.datetime.now()):
        self.id = str(uuid.uuid1())
        self.text = text
        self.value = value
        self.created_at = created_at