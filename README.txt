JSONRPC 2.0 client over HTTP

Usage
client = Client({
    "strJSONRPCRouterURL": "https://gurujsonrpc.appspot.com/guru"
})

response = client.rpc("guru.test", ["guru"])
assert ("Hello guru!" == response)
