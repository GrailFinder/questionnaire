from weakref import WeakKeyDictionary
import datetime

from pymongo import MongoClient
from nameko.extensions import DependencyProvider
from nameko.exceptions import safe_for_serialization
import os



class MongoDatabase(DependencyProvider):

    def __init__(self, result_backend=True):
        self.result_backend = result_backend
        self.logs = WeakKeyDictionary()
        
    def setup(self):

        self.client = MongoClient(os.environ.get("MONGO_URL"))

        self.db = self.client.answers

        if self.result_backend:
            self.db.logging.create_index('start', expireAfterSeconds=24*60*60)
            self.db.logging.create_index('call_id')

    def stop(self):
        self.client.close()
        del self.client

    def get_dependency(self, worker_ctx):
        return self.db
    
    def worker_setup(self, worker_ctx):
        if self.result_backend:
            self.logs[worker_ctx] = datetime.datetime.now()

            service_name = worker_ctx.service_name
            method_name = worker_ctx.entrypoint.method_name
            call_id = worker_ctx.call_id

            self.db.logging.insert_one(
                {
                    'call_id': call_id,
                    'service_name': service_name,
                    'method_name': method_name,
                    'status': 'PENDING',
                    'start': self.logs[worker_ctx]
                }
            )

    def worker_result(self, worker_ctx, result=None, exc_info=None):
        if self.result_backend:
            call_id = worker_ctx.call_id

            if exc_info is None:
                status = 'SUCCESS'
            else:
                status = 'FAILED'

            now = datetime.datetime.now()

            start = self.logs.pop(worker_ctx)

            self.db.logging.update_one(
                {'call_id': call_id},
                {
                    '$set': {
                        'status': status,
                        'end': now,
                        'elapsed': (now - start).seconds,
                        'exception': safe_for_serialization(exc_info) if exc_info is not None else None
                    }
                }
            )