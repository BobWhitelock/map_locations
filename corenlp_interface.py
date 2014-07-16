import jsonrpclib
from simplejson import loads

server = jsonrpclib.Server("http://localhost:1234")

result = loads(server.parse("Let's go to London."))
print(result)