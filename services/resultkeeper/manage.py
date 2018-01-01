from flask_script import Manager
from project import create_app, mongo

app = create_app()
manager = Manager(app)

@manager.command
def recreate_mongo():
    """Recreates a database."""
    mongo.drop_all()
    mongo.create_all()
    mongo.session.commit()


@manager.command
def seed_mongo():
    """get some data in mongo"""
    pass



if __name__ == '__main__':
    manager.run()