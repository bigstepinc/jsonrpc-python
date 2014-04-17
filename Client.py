import json
import urllib
import urllib2
import hmac
import hashlib
import time
import os
from urllib2 import HTTPError
from JSONRPC_Exception import JSONRPC_Exception
from filters.client.SignatureAdd import JSONRPC_filter_signature_add
from pprint import pprint
import base64


class JSONRPC_client(object):

			
	"""
	* JSON-RPC protocol call ID.
	"""
	_nCallID = 0;
	
	
	"""
	* Filter plugins which extend JSONRPC_client_filter_plugin_bine.
	"""
	_arrFilterPlugins = []
	
	
	"""
	* JSON-RPC server endpoint URL
	"""
	_strJSONRPCRouterURL = ""


	
	"""
	* This is the constructor function. It creates a new instance of JSONRPC_client.
	* Example: JSONRPC_client("http://example.ro")
	*
	* @param string strJSONRPCRouterURL. The address of the server.
	* @params string strLogFilePath. This is the file path where the info messages should
	* be written. It is not mandatory, a file "CommunicationLog.log" is created by default.
	"""
	def __init__(self, strJSONRPCRouterURL, strLogFilePath = None):
		
		self._strJSONRPCRouterURL = strJSONRPCRouterURL


	
	"""
	* HTTP credentials used for authentication plugins
	"""
	_strHTTPUser = None
	_strHTTPPassword = None



	"""
	* This is the function used to set the HTTP credentials set.
	*
	* @param string strUsername. 
	* @param string strPassword.
	"""
	def setHTTPCredentials(self, strUsername, strPassword):
		assert isinstance(strUsername, str)
		assert isinstance(strPassword, str)

		self._strHTTPUser = strUsername
		self._strHTTPPassword = strPassword	


	"""
	* This is the main function to call the RPC API.
	* Example: _rpc("test", "34")
	*
	* @param string strFunctionName.This is the name of the API function to be called.
	* @param array arrParams. The paramaters that the function receives.
	*
	* @return JSON sent to processRAWResponse
	"""	
	def _rpc(self, strFunctionName, arrParams ):
		
		dictRequest = {
			"jsonrpc" : "2.0",
			"method" : strFunctionName,
			"params" : arrParams,
			"id" : ++self._nCallID
		}
		
		dictFilterParams = {
			"dictRequest" : dictRequest
		}

		for objFilterPlugin in self._arrFilterPlugins:
			dictRequest = objFilterPlugin.beforeJSONEncode(dictFilterParams)["dictRequest"]
		

		strRequest = json.dumps(dictRequest)
		strEndPointURL = self._strJSONRPCRouterURL
				
		dictHTTPHeaders = {
			"Content-Type": "application/json"
		}

		if self._strHTTPUser is not None and self._strHTTPPassword is not None:
			dictHTTPHeaders["Authorization"] = "Basic "+base64.b64encode(self._strHTTPUser+":"+self._strHTTPPassword)

		dictFilterParams = {
			"strJSONRequest" : strRequest,
			"strEndpointURL" : self._strJSONRPCRouterURL, 
			"dictHTTPHeaders" : dictHTTPHeaders
		}

		for objFilterPlugin in self._arrFilterPlugins:
			if objFilterPlugin.afterJSONEncode(dictFilterParams) is not None:
				strEndPointURL = objFilterPlugin.afterJSONEncode(dictFilterParams)["strEndpointURL"]		

		bErrorMode = False
		bCalled = False

		dictFilterParams = {
			"strJSONRequest" : strRequest,
			"strEndpointURL" : strEndPointURL,
			"bCalled" : bCalled
		}

		for objFilterPlugin in self._arrFilterPlugins:
			strResult = objFilterPlugin.makeRequest(dictFilterParams)

			if bCalled:
				break

					
		if bCalled == False:	

			objRequest = urllib2.Request(strEndPointURL, headers = dictHTTPHeaders, data = strRequest)

			try:
				objFile = urllib2.urlopen(objRequest)
				strResult = objFile.read()

			except urllib2.HTTPError, objError:
				bErrorMode = True
	   	 		strResult = objError.read()
		
		return self.processRAWResponse(strResult, bErrorMode)

	

	"""
	* This is the function used to decode the received JSON and return its result.
	* It is automatically called by _rpc.
	*
	* @param object strResult. It represents the received JSON.
	* @param boolean bErrorMode. Whether or not the received JSON 
	* contains errors.
	* 
	* @return mixed mxResponse["result"]. This is the sever response result. 
	"""
	def processRAWResponse(self, strResult, bErrorMode = False):

		try:
		
			mxResponse = None

			dictFilterParams = {
				"strJSONResponse" : strResult
			}

			for objFilterPlugin in self._arrFilterPlugins:
				objFilterPlugin.beforeJSONDecode(dictFilterParams)
				
			try:
				mxResponse = json.loads(dictFilterParams["strJSONResponse"])
								
			except Exception, objError:
				raise JSONRPC_Exception(objError.message+". RAW response from server: "+dictFilterParams["strJSONResponse"], JSONRPC_Exception.PARSE_ERROR)
			
			dictFilterParams = {
				"strJSONResponse" : strResult,
				"dictResponse" : mxResponse
			}
			
			for objFilterPlugin in self._arrFilterPlugins:
				objFilterPlugin.afterJSONDecode(dictFilterParams["dictResponse"])

						
			if isinstance(mxResponse, dict)==False or (bErrorMode == True and mxResponse.has_key("error") == False):
				raise  JSONRPC_Exception("Invalid response structure. RAW response: "+dictFilterParams["strJSONResponse"], JSONRPC_Exception.INTERNAL_ERROR)
			
			elif mxResponse.has_key("result") == True and mxResponse.has_key("error") == False and bErrorMode == False:
				return mxResponse["result"]
			
			raise JSONRPC_Exception(str(mxResponse["error"]["message"]), int(mxResponse["error"]["code"]))
			
		except JSONRPC_Exception, objError:
		
			for objFilterPlugin in self._arrFilterPlugins:
				objFilterPlugin.exceptionCatch(objError)

			raise objError

		
	
	"""
	* This is a magic function, which facilitates the lookup for JSONRPC_client class attributes.
	* In order to be able to call whitelisted server functions, they are defined as class attributes
	* through the medium of the function __call.
	* If the function is not whitelisted, an exception is thrown.
	*
	* @param string strFunctionName. This is the name of the function to be called.
	*
	* @return object __call. The new defined function.
	"""
	def __getattr__(self, strClassAttribute):

					
		"""
		* This is a local function, which is used to define a function in a class attributes
		* for JSONRPC_client, based on its name and array of paramaters
		* 
		* @param *arrParam. It allows you to pass an arbitrary number of parameters, no matter their type.
		*
		* @return the result of the _rpc function 
		"""
		def __call(*tupleParams):

			arrParams = list(tupleParams)
							
			return self._rpc(strClassAttribute, arrParams)

			
		return __call

	

	"""
	* This function is used to add filter plugins to an instance of JSONRPC_client.
	* If there is an attempt to add multiple instances of the same filter,
	* an exception is thrown.
	*
	* @param object objFilterPlugin. The class of this object should extend the 
	* JSONRPC_client_filter_plugin_base class.
	"""
	def addFilterPlugin(self, objFilterPlugin):

		for objFilterPluginExisting in self._arrFilterPlugins:

			if objFilterPluginExisting.__class__ == objFilterPlugin.__class__:
				raise Exception("Multiple instances of the same filter are not allowed.")
	
		self._arrFilterPlugins.append(objFilterPlugin)
		
	
	
	"""
	* This function is used to remove client filter plugins.
	* If there is an attempt to remove an unregistered filter plugin,
	* an exception is thrown.
	*
	* @param object objFilterPlugin. The class of this object should extend the 
	* JSONRPC_client_filter_plugin_base class.
	"""
	def removeFilterPlugin(self, objFilterPlugin):
	
		nIndex = None

		for i in range(len(self._arrFilterPlugins)):
			
			if objFilterPlugin.__class__ == self._arrFilterPlugins[i].__class__:
				nIndex = i
				break
			
		if isinstance(nIndex, int) == False:
			raise Exception("Failed to remove filter plugin object, maybe plugin is not registered.")
		
		del self._arrFilterPlugins[nIndex]


	"""
	* This function is used to list all the API functions.
	"""
	def rpcFunctions(self):
		return self._rpc("rpc.functions", [])



	"""
	* This function is used to return a specific rpcReflectionFunction of the API.
	*
	* @param string strFunctionName.
	"""
	def rpcReflectionFunction(self, strFunctionName):
		return self._rpc("rpc.rpcReflectionFunction", [strFunctionName])



	"""
	* This function is used to return specific rpcReflectionFunctions of the API.
	*
	* @param array arrFunctionNames. 
	"""
	def rpcReflectionFunctions(self, arrFunctionNames):
		return _rpc("rpc.reflectionFunctions", [arrFunctionNames])