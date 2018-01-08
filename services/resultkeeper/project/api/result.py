from nameko.rpc import rpc, RpcProxy
from project import mongo

class ServiceX:
    name = "service_x"

    @rpc
    def write_to_mongo(self, value):
        return "get from flask {}, okay".format(value)
