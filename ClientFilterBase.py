"""
* JSON-RPC 2.0 client filter plugin base class.
* This is the class every other client filter plugin class should extend.
"""

class ClientFilterBase(object):


	def __init__(self):
		return
		
	
		
	"""
	* Should be used to 
	* - add extra request object keys;
	* - translate or encode output params into the expected server request object format.
	*
	* @param dictionary dictRequest. It is used for reference return for multiple variables,
	* which can be retrieved using specific keys
	* - "dictRequest"  
	*
	* @return dict dictRequest
	"""
	def beforeJSONEncode(self, dictRequest):
		return
	
	
	
	"""
	* Should be used to 
	* - encrypt, encode or otherwise prepare the JSON request string into the expected server input format;
	* - log raw output.
	*
	* @param str strJSONRequest.
	* @param str strEndpointURL.
	* @param dict dictHTTPHeaders. 
	*
	* @return dict dictHTTPHeaders
	"""
	def afterJSONEncode(self, strJSONRequest, strEndpointURL, dictHTTPHeaders):
		return
	
	
		
	"""
	* First plugin to make a request will be the last one. The respective plugin MUST set bCalled to true.
	*
	* @param str strJSONRequest.
	* @param str strEndpointURL
	* @param bool bCalled. It is used for reference return for multiple variables,
	* which can be retrieved using specific keys
	*
	* @return "mixed". The RAW string output of the server or false on error (or can throw).
	"""
	def makeRequest(self, strJSONRequest, strEndpointURL, bCalled):
		return
	
	

	"""
	* Should be used to 
	* - decrypt, decode or otherwise prepare the JSON response into the expected JSON-RPC client format;
	* - log raw input.
	*
	* @param str strJSONResponse. It is used for reference return for multiple variables,
	* which can be retrieved using specific keys
	"""
	def beforeJSONDecode(self, strJSONResponse):
		return
	
	
		
	"""
	* Should be used to 
	* - add extra response object keys;
	* - translate or decode response params into the expected JSON-RPC client response object format.
	*
	* @param dictionary dictResponse.
	"""
	def afterJSONDecode(self, dictResponse):
		return dictResponse
	


	"""
	* Should be used to rethrow exceptions as different types.
	* The first plugin to throw an exception will be the last one.
	* If there are no filter plugins registered or none of the plugins have thrown an exception,
	* then JSONRPC_Client will throw the original JSONRPC_Exception.
	*
	* @param Error exception.
	*
	* @return exception
	"""
	def exceptionCatch(self, exception):
		return exception
	
	

