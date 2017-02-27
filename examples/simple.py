from jsonrpc2base.client import Client

client = Client({
    "strJSONRPCRouterURL": "https://gurujsonrpc.appspot.com/guru"
})

response = client.rpc("guru.test", ["guru"])
assert ("Hello guru!" == response)
