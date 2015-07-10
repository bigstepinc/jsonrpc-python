import Server
from Filters.Server.ReflectionPlugin import ReflectionPlugin
#from Filters.Server.ProcessForker import ProcessForker

def test():
	#create a Server
	a = Server.JSONRPC_Server()

	#test it's members
	assert a.arrAllowedFunctionCalls == []
	assert a.arrAllowedFunctionCallsFor_HTTP_OPTIONS == []
	assert a.arrExceptionTypesForCodes == ["JSONRPC\\Exception"]
	assert a.arrExceptionTypesForMessages == ["JSONRPC\\Exception"]
	assert a.bAuthenticated == False
	assert a.bAuthorized == False
	assert a.arrFilterPlugins == []
	assert a.nHTTPResponseCode == 0
	assert a.bNotificationMode == False
	assert a.bValidateTypes == False
	assert a.arrFunctionReflection == None
	assert a.dictMethodsMappers == []

	#also print them	
	"""
	print a.arrAllowedFunctionCalls
	print a.arrAllowedFunctionCallsFor_HTTP_OPTIONS
	print a.arrExceptionTypesForCodes
	print a.arrExceptionTypesForMessages
	print a.bDebugAllowAllExceptionMessages
	print a.bAuthenticated
	print a.bAuthorized
	print a.arrFilterPlugins
	print a.strErrorLogFilePath
	print a.nHTTPResponseCode
	print a.bNotificationMode
	print a.bValidateTypes
	print a.arrFunctionReflection
	print a.dictMethodsMappers
	"""

	#null request
	#print a.processRequestAndReturn()

	#valid request before configuration of server
	strJSONRequest = '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}'
	print a.processRequestAndReturn(strJSONRequest)

	#add plugins and test them
	reflectionPlugin = ReflectionPlugin()
	#processForker = ProcessForker()
	a.addFilterPlugin(reflectionPlugin)
	#a.addFilterPlugin(processForker)

	print a.processRequestAndReturn(strJSONRequest)

test()
