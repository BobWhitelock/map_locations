#!/usr/bin/python

import jsonrpclib
from simplejson import loads

PORT = 8080

# connect to server
server = jsonrpclib.Server("http://localhost:{}".format(PORT))

result = loads(server.parse("Let's go to London."))
print(result)