"""
* JSON-RPC 2.0 client filter plugin.
* Adds authentication and signed request expiration for the JSONRPC ResellerDomainsAPI.
* Also translates thrown exceptions.
"""

import hmac
import json
import urllib2
import sys
sys.path.append("../..")
import urllib
import hashlib
import time
from ...ClientFilterBase import JSONRPC_client_filter_plugin_base
from pprint import pprint

class JSONRPC_filter_signature_add(JSONRPC_client_filter_plugin_base):


	"""
	* Private key used for hashed messages sent to the server
	"""
	strAPIKEY = ""


	"""
	* User ID
	"""
	nUserID = 0

	"""
	* This is the constructor function. It creates a new instance of JSONRPC_filter_signature_add.
	* Example: JSONRPC_filter_signature_add("secretKey")
	*
	* @param string strKEY. The private key used for hashed messages sent to the server.
	"""

	def __init__(self, strKey):

		self.strAPIKey = strKey
		self.nUserID = strKey[0:strKey.find(':')]



	"""
	* This function sets an uptime for the request.
	*
	* @param dictionary dictFilterParams. It is used for reference return for multiple variables,
	* which can be retrieved using specific keys
	* -"dictRequest"
	*
	* @return dict dictFilterParams
	"""
	def beforeJSONEncode(self, dictFilterParams):

		dictFilterParams["dictRequest"]["expires"] = int(time.time()+86400)

		return dictFilterParams




	"""
	* This function is used for authentication. It alters the Endpoint URL such that it contains
	* a specific signature.
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

		strVerifyHash = hmac.new(self.strAPIKey, dictFilterParams["strJSONRequest"], hashlib.md5).hexdigest()
		
		if dictFilterParams["strEndpointURL"].find('?') != -1:
			dictFilterParams["strEndpointURL"] += "&"

		else:
			dictFilterParams["strEndpointURL"] += "?"

		if dictFilterParams["strEndpointURL"].find("?verify") == -1:
			dictFilterParams["strEndpointURL"] += "verify="+urllib.quote(strVerifyHash)+"&user_id="+str(self.nUserID)
		
		if dictFilterParams["strEndpointURL"][-1] == '&':
			dictFilterParams["strEndpointURL"] = dictFilterParams["strEndpointURL"][:-1]

		
		return dictFilterParams

		
