from services.questmaker import db, bcrypt
import datetime, uuid
from flask import current_app
import jwt

questgroup = db.Table("questgroup",
    db.Column('questions', db.String(128), db.ForeignKey('questions.id'), primary_key=True),
    db.Column('inquiries', db.String(128), db.ForeignKey('inquiries.id'), primary_key=True)
)

inqowner = db.Table("inqowner",
    db.Column('users', db.String(128), db.ForeignKey('users.id'), primary_key=True),
    db.Column('inquiries', db.String(128), db.ForeignKey('inquiries.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(128), nullable=False, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    inquiries = db.relationship("Inquiry", secondary=inqowner, backref=db.backref('owner', lazy='dynamic'))

    def __init__(self, username, email, password):
        self.id = str(uuid.uuid1())
        self.username = username
        self.email = email
        self.created_at = datetime.datetime.now()
        self.password = bcrypt.generate_password_hash(password, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()

    def encode_auth_token(self):
        """Generates the auth token"""
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(
                days=current_app.config.get('TOKEN_EXPIRATION_DAYS'),
                seconds=current_app.config.get('TOKEN_EXPIRATION_SECONDS')),
                'iat': datetime.datetime.utcnow(),
                'jti': self.id # https://www.jsonwebtoken.io/
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """Decodes the auth token - :param auth_token: - :return: integer|string"""
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['jti']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Inquiry(db.Model): # Опросник
    __tablename__ = "inquiries"
    id = db.Column(db.String(128), nullable=False, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    description = db.Column(db.Text, nullable=True)
    questions = db.relationship("Question", secondary=questgroup, backref=db.backref('inquiry', lazy='dynamic'))

    def __init__(self, title, description=None, id=None):
        if not id:
            self.id = str(uuid.uuid1())
        else:
            self.id = id
        self.title = title
        self.description = description

    def __str__(self):
        return f'{self.title}: {self.id}'
    

class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.String(128), nullable=False, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    multichoice = db.Column(db.Boolean)
    choices = db.relationship("Choice", backref=db.backref('question', lazy=True))

    def __init__(self, title, multichoice=False, created_at=datetime.datetime.now()):
        self.id = str(uuid.uuid1())
        self.title = title
        self.created_at = created_at
        self.multichoice = multichoice

    def __str__(self):
        return f'{self.title}: {self.id}'

class Choice(db.Model):
    __tablename__ = "choices"
    id = db.Column(db.String(128), nullable=False, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    value = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    question_id = db.Column(db.String(128), db.ForeignKey('questions.id'), nullable=False)

    def __init__(self, text, question_id, value=None, created_at=datetime.datetime.now()):
        self.id = str(uuid.uuid1())
        self.text = text
        self.value = value
        self.created_at = created_at
        self.question_id = question_id

    def __str__(self):
        return f'{self.title}: {self.id}'

class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.String(128), nullable=False, primary_key=True)
    choice = db.Column(db.String(128), db.ForeignKey('choices.id'), nullable=False)
    question = db.Column(db.String(128), db.ForeignKey('questions.id'), nullable=False)
    inq = db.Column(db.String(128), db.ForeignKey('inquiries.id'), nullable=False)
    user = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=True)

    def __init__(self, **kwargs):
        #https://stackoverflow.com/questions/20460339/flask-sqlalchemy-constructor
        super(Answer, self).__init__(**kwargs) # too lazy to bind all of it
        self.id = str(uuid.uuid1())

