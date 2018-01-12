from nameko.rpc import rpc
from pymongo import MongoClient
from pymongo.database import Database
from project.dependencies import MongoDatabase

class ServiceX:
    name = "service_x"

    # @rpc
    # def write_to_mongo(self, value):
    #     return "get from flask {}, okay".format(value)

    db = MongoDatabase()

    @rpc
    def insert_one(self, document):
        res = self.db.answers.insert_one(document)
        return "{}".format(res.inserted_id)

    @rpc
    def find_one(self, query):
        doc = self.db.answers.find_one(query)
        return f"{doc}"

    @rpc
    def find(self):
        doc = self.db.answers.find()
        return str(list(doc))
