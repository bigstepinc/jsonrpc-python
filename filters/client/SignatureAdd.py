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
from ...ClientFilterBase import JSONRPC_ClientFilterBase
from pprint import pprint

class JSONRPC_filter_signature_add(JSONRPC_ClientFilterBase):


	"""
	* Private key used for hashed messages sent to the server
	"""
	strAPIKey = None


	"""
	* Extra URL variables
	"""
	dictExtraURLVariables = {}


	"""
	* Private key used for hashed messages sent to the server
	"""
	strKeyMetaData = None


	"""
	* This is the constructor function. It creates a new instance of JSONRPC_filter_signature_add.
	* Example: JSONRPC_filter_signature_add("secretKey")
	*
	* @param string strKey. The private key used for hashed messages sent to the server.
	"""

	def __init__(self, strAPIKey, dictExtraURLVariables):

		self.strAPIKey = strAPIKey
		self.dictExtraURLVariables = dictExtraURLVariables
		self._getKeyMetaData()

	def _getKeyMetaData(self):
		arrKEYSplit = self.strAPIKey.split(":", 2)
		if(arrKEYSplit.__len__() == 1):
			self.strKeyMetaData = None
		else:
			self.strKeyMetaData = arrKEYSplit[0]


	"""
	* This function sets an uptime for the request.
	*
	* @param dictionary dictRequest.
	*
	* @return dict dictRequest
	"""
	def beforeJSONEncode(self, dictRequest):

		dictRequest["expires"] = int(time.time()+86400)

		return dictRequest



	"""
	* This function is used for authentication. It alters the Endpoint URL such that it contains
	* a specific signature.
	* 
	* @param str strJSONRequest 
	* @param str strEndpointURL
	* @param str dictHTTPHeaders
	*
	* @return dict dictFilterParams?
	"""
	def afterJSONEncode(self, strJSONRequest, strEndpointURL, dictHTTPHeaders):

		strVerifyHash = hmac.new(self.strAPIKey, strJSONRequest, hashlib.md5).hexdigest()
		
		if (self.strKeyMetaData != None):
		    strVerifyHash = self.strKeyMetaData + ":" + strVerifyHash
		
		if (strEndpointURL.find('?') != -1):
			strEndpointURL += "&"
		else:
			strEndpointURL += "?"

		if (strEndpointURL.find("?verify") == -1):
			strEndpointURL += "verify=" + urllib.quote(strVerifyHash);

		for key, value in self.dictExtraURLVariables.items():
			value = str(value)
			strEndpointURL += "&" + urllib.quote(key) + "=" + urllib.quote(value)		
		
		return dictFilterParams

		
