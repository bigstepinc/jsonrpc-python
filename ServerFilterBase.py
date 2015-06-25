class JSONRPC_ServerFilterBase(object):
	def __init__(self):
	{
	}		

		
	"""
	* Should be used complementary to the authorization on JSONRPC_Server.arrAllowedFunctionCalls.
	* This function is called before JSONRPC_ServerFilterBase.resolveFunctionName.
	* @param string strFunctionName.
	"""
	def isFunctionNameAllowed(self, strFunctionName):
		return False
		
		
	"""
	* Should be used to 
	* - decrypt or decode an input (binary or string) into the expected JSONRPC_Server JSON input format;
	* - log raw input.
	* @param string strJSONRequest.
	"""
	"""WARNING: Removed & reference"""
	def beforeJSONDecode(self, strJSONRequest):
		pass
		
		
	"""
	* Should be used to 
	* - add authorization and authentication based on param values within the JSON request;
	* - translate or decode input params into the expected JSONRPC_Server array input format.
	* Upon successfull authentication this function must set JSONRPC_Server.bAuthenticated to true.
	* Upon successfull authorization this function must set JSONRPC_Server.bAuthorized to true.
	* @param array arrRequest.
	* @param string strJSONRequest.
	"""
	"""WARNING: Removed & reference"""
	def afterJSONDecode(self, arrRequest):
		pass
		
		
	"""
	* Should be used to update the JSONRPC_Server response with additional info.
	* @param array arrJSONRPCResponse. Associative array in JSONRPC_Server response.
	"""
	def response(self, arrJSONRPCResponse):
		pass
		
		
	"""
	* Translates an API declared function name to an internally callable function name.
	* @param string strFunctionName.
	"""
	"""WARNING: Removed & reference"""
	def resolveFunctionName(strFunctionName):
		pass		
		
	"""
	* Should wrap call_user_func_array to allow for custom centralised error handling 
	* with/and function call retries, before returning to RPC client (and other uses).
	*
	* Caller (JSONRPC_Server) is responsible for not calling strFunctionName more than once
	* (first plugin enountered to implement this filter which returned true in bCalled must be the only one to make a call).
	*
	* Plugins are responsible of making sure bCalled is set to true if an attempt is made to call the function, 
	* even if an unhandled or handled exception occurs.
	*
	* @param string strFunctionName.
	* @param array arrParams.
	* @param bool bCalled. Return param. True if the function in strFunctionName was called, oterwise false.
	* @return mixed. Returns the call_user_func_array result with bCalled set to true. Otherwise returns None and bCalled will be set to False.
	"""
	"""WARNING: Removed & reference"""
	def callFunction(self, strFunctionName, arrParams, bCalled):
		assert bCalled is False			
		bCalled = False
		
		
	"""
	* Should be used to rethrow exceptions as different types.
	* The first plugin to throw an exception will be the last one.
	* If there are no filter plugins registered or none of the plugins have thrown an exception,
	* then Client will throw the original Exception.
	* @param Exception exception.
	"""
	def exceptionCatch(self, exception):
		pass


		
	"""
	* This should be used to assign the server object
	* @param JSONRPC_Server server.
	"""
	def setServerInstance(server): 
		pass