"""
* JSON-RPC 2.0 client filter plugin base class.
* This is the class every other client filter plugin class should extend.
"""

class JSONRPC_client_filter_plugin_base:



	def __construct(self):

		return
		
	
	
		
	"""
	* Should be used to 
	* - add extra request object keys;
	* - translate or encode output params into the expected server request object format.
	*
	* @param dictionary dictFilterParams. It is used for reference return for multiple variables,
	* which can be retrieved using specific keys
	* - "dictRequest"  
	*
	* @return dict dictFilterParams
	"""
	def beforeJSONEncode(self, dictFilterParams):
		return dictFilterParams
	
	
	
	"""
	* Should be used to 
	* - encrypt, encode or otherwise prepare the JSON request string into the expected server input format;
	* - log raw output.
	*
	* @param dictionary dictFilterParams. It is used for reference return for multiple variables,
	* which can be retrieved using specific keys
	* - "strJSONRequest"
	* - "strEndpointURL"
	* - "dictHTTPHeaders"
	*
	* @return dict dictFilterParams
	"""
	def afterJSONEncode(self, dictFilterParams):
		return dictFilterParams
	
	
		
	"""
	* First plugin to make a request will be the last one. The respective plugin MUST set bCalled to true.
	*
	* @param dictionary dictFilterParams. It is used for reference return for multiple variables,
	* which can be retrieved using specific keys
	* - "mixed". The RAW string output of the server or false on error (or can throw).
	*
	* @return dict dictFilterParams
	"""
	def makeRequest(self, dictFilterParams):
		return dictFilterParams
	
	

	"""
	* Should be used to 
	* - decrypt, decode or otherwise prepare the JSON response into the expected JSON-RPC client format;
	* - log raw input.
	*
	* @param dictionary dictFilterParams. It is used for reference return for multiple variables,
	* which can be retrieved using specific keys
	* - "strJSONResponse"
	*
	* @return dict dictFilterParams
	"""
	def beforeJSONDecode(self, dictFilterParams):
		return dictFilterParams
	
	
		
	"""
	* Should be used to 
	* - add extra response object keys;
	* - translate or decode response params into the expected JSON-RPC client response object format.
	*
	* @param dictionary dictFilterParams. It is used for reference return for multiple variables,
	* which can be retrieved using specific keys
	* - "dictResponse"
	*
	* @return dict dictFilterParams
	"""
	def afterJSONDecode(self, dictFilterParams):
		return dictFilterParams
	


	"""
	* Should be used to rethrow exceptions as different types.
	* The first plugin to throw an exception will be the last one.
	* If there are no filter plugins registered or none of the plugins have thrown an exception,
	* then JSONRPC_client will throw the original JSONRPC_Exception.
	*
	* @param Error exception.
	*
	* @return exception
	"""
	def exceptionCatch(self, exception):
		return exception
	
	

