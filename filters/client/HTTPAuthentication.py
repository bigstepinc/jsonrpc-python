"""
* JSON-RPC 2.0 client filter plugin.
* Adds authentication based on credentials sent through  HTTP Authorization header.
* Also translates thrown exceptions.
"""

import base64
from ...ClientFilterBase import JSONRPC_client_filter_plugin_base


class JSONRPC_filter_authorization_header_add(JSONRPC_client_filter_plugin_base):



	"""
	* This is the constructor function. It creates a new instance of JSONRPC_filter_authorization_header_add.
	* Example: JSONRPC_filter_authorization_header_add("user", "pass")
	*
	* @param string strUsername 
	* @param string strPassword 
	"""
	def __init__(self, strUsername, strPassword):

		self.strUsername = strUsername
		self.strPassword = strPassword



	"""
	* This function is used for basic HTTP authentication. It adds a HTTP Authorization header to 
	* the request.
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

		strAuthentication = base64.b64encode(self.strUsername+":"+self.strPassword)
		dictFilterParams["dictHTTPHeaders"]["Authorization"] = "Basic "+strAuthentication