from services.questmaker import db
import datetime, uuid


answbond = db.Table("answbond",
    db.Column('questions', db.String(128), db.ForeignKey('questions.id'), primary_key=True),
    db.Column('answers', db.String(128), db.ForeignKey('answers.id'), primary_key=True)
)

questgroup = db.Table("questgroup",
    db.Column('questions', db.String(128), db.ForeignKey('questions.id'), primary_key=True),
    db.Column('inquiries', db.String(128), db.ForeignKey('inquiries.id'), primary_key=True)
)


class Inquiry(db.Model): # Опросник
    __tablename__ = "inquiries"
    id = db.Column(db.String(128), nullable=False, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)
    questions = db.relationship("Question", secondary=questgroup, backref=db.backref('inquiry', lazy='dynamic'))

    def __init__(self, title, description=None, created_at=datetime.datetime.now()):
        self.id = str(uuid.uuid1())
        self.title = title
        self.created_at = created_at
        self.description = description
    

class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.String(128), nullable=False, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    multiansw = db.Column(db.Boolean)
    answers = db.relationship("Answer", secondary=answbond, backref=db.backref('question', lazy='dynamic'))

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