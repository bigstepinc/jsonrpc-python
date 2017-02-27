JSONRPC 2.0 client over HTTP

Usage:
client = Client({
    "strJSONRPCRouterURL": "your-url-here"
})
response = client.rpc("test", ["param1", "param2"])
