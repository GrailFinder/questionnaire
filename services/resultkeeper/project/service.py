from nameko.rpc import rpc, RpcProxy

class ServiceX:
    name = "service_x"

    @rpc
    def write_to_mongo(self, value):
        return "get from flask {}, okay".format(value)
