import os
import sys
import json
import traceback
import re
from urlparse import urlparse
import httplib
from JSONRPC_Exception import JSONRPC_Exception
from Filters.Server.ReflectionPlugin import ReflectionPlugin

class JSONRPC_Server(object):
	
	def __init__(self):
		pass
		
	"""
	* Exposed RPC function names.
	* 
	* This array should not appear in stack traces (it is cumbersome, and is a security issue), 
	* that's why it is not passed as a param.
	* 
	* @var array
	*
	"""
	arrAllowedFunctionCalls = []


	"""
	* Exposed RPC function names which are known to handle the OPTIONS HTTP method.
	* 
	* This array should not appear in stack traces (it is cumbersome, and is a security issue), 
	* that's why it is not passed as a param.
	* 
	* @var array
	"""
	arrAllowedFunctionCallsFor_HTTP_OPTIONS = []

		
	"""
	* RPC Exception codes are allowed in the response by checking the Exception type.
	*
	* Must not contain root namespace backslash.
	*
	* @var array
	"""
	arrExceptionTypesForCodes = ["JSONRPC\\Exception"]

		
	"""
	* RPC Exception messages are allowed in the response by checking the Exception type.
	* 
	* Must not contain root namespace backslash.
	* 
	* @var array
	"""
	"""WARNING: ???"""
	arrExceptionTypesForMessages = ["JSONRPC\\Exception"]
		
		
	"""
	* Debug aid.
	* If true, it overrides ::arrExceptionTypesForMessages and all exception messages are allowed.
	* Should not be used on production servers.
	* @var bool
	"""
	bDebugAllowAllExceptionMessages = True
		
		
	"""
	* Simple safe-guard. Must be set to true after successfull authentication.
	* 
	* @var bool
	"""
	bAuthenticated = False
		
		
	"""
	* Simple safe-guard. Must be set to true after successfull authorization.
	* 
	* @var bool
	"""
	bAuthorized = False
		
		
	"""
	* Filter plugins which extend JSONRPC_ServerFilterBase.
	* 
	* @var array
	"""
	arrFilterPlugins = []

		
	"""
	* JSONRPC log file path.
	* 
	* @var string
	"""
	strErrorLogFilePath = "C:\ExportVHosts\jsonrpc-python\logger.txt"
		
		
	"""
	* HTTP response code.
	* 
	* @var int
	"""
	nHTTPResponseCode = 0
		
		
	"""
	* Wether serving a Notification request.
	* 
	* @var bool
	"""
	bNotificationMode = False
		
		
	"""
	* If true, it will validate input types.
	* 
	* @var bool
	"""
	bValidateTypes = False
		

	"""WARNING: Correct coding style"""
	"""
	* As returned by \JSONRPC\Filters\Server\ReflectionPlugin::reflectionFunction().
	* 
	* @var array
	"""
	arrFunctionReflection = None
		
		
	"""WARNING: Correct coding style"""
	"""
	* Associative array with class names as keys and JSONRPC\MethodsMapper instances as values.
	* 
	* @var array
	"""
	dictMethodsMappers = []
		
		
	def processRequest(self, strJSONRequest = None):
		self._exitWithResponse(self.processRequestAndReturn(strJSONRequest))

		
		
	def processRequestAndReturn(self, strJSONRequest = None):
		objReflectionPlugin = ReflectionPlugin()
		objReflectionPlugin.setServerInstance(self);

		if os.environ.get("REQUEST_METHOD") != None and os.environ.get("REQUEST_METHOD") not in ("GET", "POST", "PUT", "OPTIONS"):
				print "HTTP request method " + os.environ.get("REQUEST_METHOD") + " ignored."
				sys.exit(0)

		"""WARNING: Check type of mxRequestID"""
		mxRequestID = None
		try:
			"""//php://input must be read here only for normal HTTP POST JSON-RPC requests."""
			if (strJSONRequest == None and (os.environ.get("REQUEST_METHOD") == None) or os.environ.get("REQUEST_METHOD") == "POST"):
				strJSONRequest = raw_input()
			
			for plugin in self.arrFilterPlugins: 
				plugin.beforeJSONDecode(strJSONRequest)

				
			"""WARNING: Fix coding style"""
			if (len(strJSONRequest.strip()) == 0):
				raise JSONRPC_Exception("Invalid request. Empty input. Was expecting a POST request of a JSON.", JSONRPC_Exception.PARSE_ERROR)

			print "From Server with love " + strJSONRequest

			"""TODO: Add a hook to change unicode to ascii"""
			dictRequest = json.loads(strJSONRequest, object_hook = self._decode_dict)
			print str(dictRequest)
			"""
			for k, v in dictRequest:
				print k + '[' + v + ']'
			"""

			"""WARNING: May have a problem at indexation in dictionaries"""	
			if ('0' in dictRequest.keys() and dictRequest[0] != None):
				raise JSONRPC_Exception("JSON-RPC batch requests are not supported by this server.", JSONRPC_Exception.INVALID_REQUEST)
					

			if (("method" in dictRequest and dictRequest["method"] != None) and isinstance(dictRequest["method"], basestring) and \
							 (len(dictRequest["method"].strip()) != 0) and ("params" in dictRequest.keys())):
				self.arrFunctionReflection = None

				try:
					self.arrFunctionReflection = objReflectionPlugin.reflectionFunction(dictRequest["method"])

				except Exception:
					"""
					 * Ignoring because the reflection is expected to sometimes fail here.
					 * The reflection will be retried later where it is not expected to fail.
					 * One of these tries must succeed to obtain the functions reflection object.
					"""
					pass

				if (self.arrFunctionReflection != None):
					self.namedParamsTranslationAndValidation(self.arrFunctionReflection["function_params"], dictRequest["params"], dictRequest["method"])
					self.validateDataTypes(self.arrFunctionReflection["function_params"], dictRequest["params"])
				
			for plugin in self.arrFilterPlugins: 
				plugin.afterJSONDecode(dictRequest)
			

			#A String containing the name of the method to be invoked. 
			#Method names that begin with the word rpc followed by a period character (U+002E or ASCII 46)
			#are reserved for rpc-internal methods and extensions and MUST NOT be used for anything else.
			if (
				("method" in dictRequest and dictRequest["method"] == None) \
				or (not isinstance(dictRequest["method"], basestring)) \
				or (len(dictRequest["method"].strip()) == 0)
			):
				raise JSONRPC_Exception("The \"method\" key must be a string with a function name.", JSONRPC_Exception.INVALID_REQUEST)
				
				
				
			#A Structured value that holds the parameter values to be used during the invocation of the method.
			#This member MAY be omitted.
			if ("params" not in dictRequest.keys()):
				"""WARNING: Not sure if this is [] or None"""
				dictRequest["params"] = None
				
			if (not isinstance(dictRequest["params"], list)):
				raise JSONRPC_Exception("The \"params\" key must be an array.", JSONRPC_Exception.INVALID_REQUEST);


			if (("method" in dictRequest and hasattr(dictRequest["method"], '__call__')) or ("method" in dictRequest and dictRequest["method"] != None)):
				self.arrFunctionReflection = objReflectionPlugin.reflectionFunction(dictRequest["method"])
				self.namedParamsTranslationAndValidation(self.arrFunctionReflection["function_params"], dictRequest["params"], dictRequest["method"])
				self.validateDataTypes(self.arrFunctionReflection["function_params"], dictRequest["params"])
			

			if (os.environ["REQUEST_METHOD"] != None and os.environ["REQUEST_METHOD"] == "OPTIONS" \
				and dictRequest["method"] not in self.arrAllowedFunctionCallsFor_HTTP_OPTIONS):
				print "HTTP request method " + os.environ["REQUEST_METHOD"] + " ignored."
				sys.exit(0)


			#An identifier established by the Client that MUST contain a String, Number, or NULL value if included. 
			#If it is not included it is assumed to be a notification. 
			#The value SHOULD normally not be Null and Numbers SHOULD NOT contain fractional parts.
			self.bNotificationMode = "id" not in dictRequest
				
			if ((not self.bNotificationMode) and (not isinstance(dictRequest["id"], int)) and ("id" in dictRequest and dictRequest["id"] != None)):
				raise JSONRPC_Exception("The \"id\" key must be an integer, a null or be omitted for Notification requests.", JSONRPC_Exception.INVALID_REQUEST)
				
			if (not self.bNotificationMode):
				"""WARNING: Check mxRequestID type"""
				mxRequestID = dictRequest["id"]
				
				
				
			#A String specifying the version of the JSON-RPC protocol. MUST be exactly "2.0".
			if (("jsonrpc" not in dictRequest or dictRequest["jsonrpc"] == None) or ("jsonrpc" not in dictRequest or dictRequest["jsonrpc"] != self.JSONRPC_VERSION)):
				raise JSONRPC_Exception("The \"jsonrpc\" version must be equal to " + self.JSONRPC_VERSION, JSONRPC_Exception.INVALID_REQUEST)
				
				
				
			"""WARNING: Could throw exception on trying to access non-existant "method" key"""
			self.assertFunctionNameAllowed(dictRequest.get("method"))
				
				
				
			#Safe-guard, so developers don't accidentally open the RPC server to the world (default is false, not authenticated).
			#Exceptions should be thrown by authentication filters.
			#Authentication filters must set JSONRPC_server::$bAuthenticated to true upon successfull authentication.
			if (not self.bAuthenticated):
				raise JSONRPC_Exception("Not authenticated (bad credentials or signature).", JSONRPC_Exception.NOT_AUTHENTICATED)
				
				
			#Safe-guard, so developers don't accidentally open the RPC server to any user account (default is false, not authorized).
			#Exceptions should be thrown by authorization filters.
			#Authorization filters must set JSONRPC_server::$bAuthorized to true upon successfull authorization.
			if (not self.bAuthorized):
				raise JSONRPC_Exception("Authenticated user is not authorized.", JSONRPC_Exception.NOT_AUTHORIZED)
					
				
			dictResponse = {"result" : None}
			dictResponse["result"] = self.callFunction(dictRequest["method"], dictRequest["params"])
				
			if ((self.arrFunctionReflection != None) and len(self.arrFunctionReflection) != 0):
				self.returnDataTypeValidation(dictRequest["method"], self.arrFunctionReflection["function_return_type"], dictResponse["result"])

			if (self.nHTTPResponseCode == 0):
				if (self.bNotificationMode == True):
					self.nHTTPResponseCode = self.HTTP_204_NO_CONTENT
				else:
					self.nHTTPResponseCode = self.HTTP_200_OK
			
		
		except Exception as exc:
			try:
				self._log_exception(exc)
					
				#Gives a chance to log the original Exception and/or throw another "translated" Exception.
				#If nothing is thrown inside exceptionCatch, this catch block will rethrow the original Exception anyway.
				for plugin in self.arrFilterPlugins:
					plugin.exceptionCatch(exc)
				"""TODO"""
				#raise exc
				dictResponse = self._exceptionToJSONResponse(exc)

			except Exception as exc:
				dictResponse = self._exceptionToJSONResponse(exc)
			
			
		dictResponse["jsonrpc"] = self.JSONRPC_VERSION
		if (not self.bNotificationMode):
			dictResponse["id"] = mxRequestID
		try:
			for plugin in self.arrFilterPlugins:
				plugin.response(dictResponse)
		except Exception as exc:
			self._log_exception(exc)

			if ("error" not in dictResponse or dictResponse["error"] == None):
				dictResponse = self._exceptionToJSONResponse(exc)
			
		return dictResponse


	def _decode_list(self, data):
		rv = []
		for item in data:
			if isinstance(item, unicode):
				item = item.encode('utf-8')
			elif isinstance(item, list):
				item = _decode_list(item)
			elif isinstance(item, dict):
				item = _decode_dict(item)
			rv.append(item)
		return rv

	def _decode_dict(self, data):
		rv = {}
		for key, value in data.iteritems():
			if isinstance(key, unicode):
				key = key.encode('utf-8')
			if isinstance(value, unicode):
				value = value.encode('utf-8')
			elif isinstance(value, list):
				value = self._decode_list(value)
			elif isinstance(value, dict):
				value = self._decode_dict(value)
			rv[key] = value
		return rv

	"""
	 * Will affect the HTTP status.
	 * @param JSONRPC_Exception exc
	"""
	def _exceptionToJSONResponse(self, exc):
		"""WARNING: Not sure if __name__ wanted or just __class__"""
		strExceptionClass = exc.__class__.__name__
		strExceptionClass = strExceptionClass.lstrip('\\')

		"""Get information about the current exception being caught"""
		excType, excValue, excTraceback = sys.exc_info()

		if (strExceptionClass in self.arrExceptionTypesForMessages):
			strMessage = exc.message
		elif (self.bDebugAllowAllExceptionMessages == True):
			"""WARNING: Check exception functions"""
			"""WARNING: Modified error message"""
			strMessage = ("[Internal error: " + " ".join(traceback.format_exception(excType, excValue, excTraceback)))
		
		else:
			strMessage = "Internal error."
				
		if (strExceptionClass in self.arrExceptionTypesForCodes):
			nCode = int(excValue)
		else:
			nCode = 0
						
		if (self.nHTTPResponseCode == 0):
			if (nCode in [JSONRPC_Exception.NOT_AUTHENTICATED, JSONRPC_Exception.NOT_AUTHORIZED]):
				self.nHTTPResponseCode = self.HTTP_403_FORBIDDEN
			else:
				self.nHTTPResponseCode = self.HTTP_500_INTERNAL_SERVER_ERROR
			
		dictResponse = {}
		dictResponse["error"] = {"message" : strMessage, "code" : nCode}

		return dictResponse

		
	def _exitWithResponse(self, dictResponse):
		self._http_response_code(self.nHTTPResponseCode)
		self._header("Cache-Control: no-cache, must-revalidate")
		self._header("Expires: Mon, 26 Jul 1991 05:00:00 GMT")
		self._header("Accept-Ranges: none")
		self._header("Connection: close")
		self._header("Content-type: application/json")
		#self::_header("Content-type: text/plain;charset=utf-8");
			
			
		"""
		* JSON-RPC 2.0 Specification, 4.1 Notification
		* Notifications are not confirmable by definition, since they do not have a Response object to be returned. 
		* As such, the Client would not be aware of any errors (like e.g. "Invalid params","Internal error").
		"""
		if (self.bNotificationMode == False):
			print json.dumps(dictResponse)
			
		if (self.nHTTPResponseCode in [self.HTTP_200_OK, self.HTTP_204_NO_CONTENT]):
			sys.exit(0)
		
		sys.exit(1)

		
	def callFunction(self, strFunctionName, dictParams):
		"""WARNING: Not sure if this ignores user abort. It shouldn't ignore it."""
		try:
			self.assertFunctionNameAllowed(strFunctionName)
			
			for plugin in self.arrFilterPlugins:
				plugin.resolveFunctionName(strFunctionName)
					
			"""WARNING: Double check/Error prone"""	
			bCalled = False
			for pluginExisting in self.arrFilterPlugins:
				mxResult = pluginExisting.callFunction(strFunctionName, dictParams, bCalled)
				if (bCalled == True):
					break
			
			if (bCalled == False):
				"""WARNING: This can be done better."""
				if (not hasattr(strFunctionName, __call__)):
					fcallable = self.functionNameToCallableArray(strFunctionName)
					mxResult = fcallable(self.array_make_references(dictParams))
				else:
					mxResult = strFunctionName(self.array_make_references(dictParams))
				
			return mxResult
		except Exception as e:
			pass
		
		
	"""
	@var plugin is of type JSONRPC_ServerFilterBase
	"""
	def addFilterPlugin(self, plugin):
		for pluginExisting in self.arrFilterPlugins:
			if (pluginExisting.__class__ == plugin.__class__):
				return
		plugin.setServerInstance(self)
		"""???"""
		self.arrFilterPlugins.append(plugin)
		
		
	"""
	@var plugin is of type JSONRPC_ServerFilterBase
	"""
	def removeFilterPlugin(self, plugin):
		nIndex = None
		"""WARNING: Modified over the original"""
		nIndexExisting = 0
		for pluginExisting in self.arrFilterPlugins:
			if (pluginExisting.__class__ == plugin.__class__):
				nIndex = nIndexExisting
				break
			else:
				nIndexExisting += 1

		if (isinstance(nIndex, int) == False):
			raise Exception("Failed to remove filter plugin object, maybe plugin is not registered.")
			
		"""WARNING: Modified over the original"""
		del self.arrFilterPlugins[nIndex]
		
		
	"""
	@var methodsMapper is of type JSONRPC_MethodsMapper.
	"""
	def addMethodsMapper(self, methodsMapper):
		for methodsMapperExisting in self.dictMethodsMappers:
			if (methodsMapperExisting == methodsMapper):
				return

		self.dictMethodsMappers[methodsMapper.instanceWithAPIMethods().__class__] = methodsMapper
		
		
	def removeMethodsMapper(self, methodsMapper):
		strInstanceAPIClassNameExisting = methodsMapper.instanceWithAPIMethods().__class__
			
		if (strInstanceAPIClassNameExisting in self.dictMethodsMappers):
			"""WARNING: Not sure if thise should be None or deleted entirely"""
			self.dictMethodsMappers[strInstanceAPIClassNameExisting] = None;
		else:
			raise Exception("Failed to remove methodsMapper object.")

		
	def methodsMappers(self):
		return self.dictMethodsMappers
		
		
	"""
	 * @param string strFunctionName
	 * 
	 * @return tuple of instance and callable array ???
	"""
	def functionNameToCallableArray(self, strFunctionName):
		for methodsMapper in self.methodsMappers():
			if (strFunctionName in methodsMapper.arrAPIFunctionsNamesToMethodsNames()):
				# Returning callable "type".
				return {0 : methodsMapper.instanceWithAPIMethods(), \
						1 : methodsMapper.arrAPIFunctionsNamesToMethodsNames()[strFunctionName]}
			
		raise JSONRPC_Exception("The function " + strFunctionName + " is not defined or loaded.", JSONRPC_Exception.METHOD_NOT_FOUND)		
		

	"""
	 * @param string strFunctionName 
	 * 
	 * @throws JSONRPC_Exception 
	 * @return None
	"""
	def assertFunctionNameAllowed(self, strFunctionName):
		bFunctionNameAllowed = False
		for plugin in self.arrFilterPlugins:
			bFunctionNameAllowed = plugin.isFunctionNameAllowed(strFunctionName)
			if (bFunctionNameAllowed == True):
				break

		if ((bFunctionNameAllowed == False) and (strFunctionName not in self.arrAllowedFunctionCalls)):
			self.nHTTPResponseCode = self.HTTP_403_FORBIDDEN
			raise JSONRPC_Exception("The function \"" + strFunctionName + "\" is not exported and/or does not exist.", JSONRPC_Exception.METHOD_NOT_FOUND)
		
		
		
	"""WARNING: Eliminated & reference"""
	"""TODO: Check if this is needed. It shouldn't be in python."""
	def array_make_references(self, arrSomething):
		arrAllValuesReferencesToOriginalValues = []
		for mxKey in arrSomething:
			arrAllValuesReferencesToOriginalValues[mxKey] = arrSomething[mxKey]
		return arrAllValuesReferencesToOriginalValues
		
		
	def _log_exception(self, exception):
		try:
			if (len(self.strErrorLogFilePath) != 0):
				strClientInfo = ""
				strError = ""
				if ("REMOTE_ADDR" in os.environ):
					strClientInfo = strClientInfo + " " + os.environ["REMOTE_ADDR"]
				if("HTTP_USER_AGENT" in os.environ):
					strClientInfo = strClientInfo + " " + os.environ["HTTP_USER_AGENT"]
					
				"""WARNING: Get exception functions"""
				try:
					excType, excValue, excTraceback = sys.exc_info()

					"""WARNING: Modified regex"""
					if (re.search('@*RECURSION*@', " ".join(str(traceback.extract_tb(excTraceback)))) != None):
						raise Exception("Recursive stack trace.")

				except Exception as exc:
					excType, excValue, excTraceback = sys.exc_info()
					strError = " ".join(traceback.format_exception(excType, excValue, excTraceback)) + os.linesep + os.linesep

				with open(self.strErrorLogFilePath, "a+") as errorLogFile:
					errorLogFile.write(strError)

		except Exception as exc:
			"""WARNING: Check format """
			excType, excValue, excTraceback = sys.exc_info()
			traceback.print_exception(excType, excValue, excTraceback)
			sys.exit(1)
		
		
	HTTP_200_OK = 200
	HTTP_204_NO_CONTENT = 204
	HTTP_401_UNAUTHORIZED = 401
	HTTP_403_FORBIDDEN = 403
	HTTP_429_TOO_MANY_REQUESTS = 429
	HTTP_500_INTERNAL_SERVER_ERROR = 500

	arrHTTPResponseCodesToText = {HTTP_200_OK : "OK",
			HTTP_204_NO_CONTENT : "No Content",
			HTTP_401_UNAUTHORIZED : "Unauthorized",
			HTTP_403_FORBIDDEN : "Forbidden",
			HTTP_429_TOO_MANY_REQUESTS : "Too Many Requests",
			HTTP_500_INTERNAL_SERVER_ERROR : "Internal Server Error"}
		
	def _http_response_code(self, nHTTPResponseCode):
		if (self.nHTTPResponseCode == 0):
			self.nHTTPResponseCode = self.HTTP_500_INTERNAL_SERVER_ERROR
				
		self._header("HTTP/1.1 " + str(int(nHTTPResponseCode)) + " " + self.arrHTTPResponseCodesToText[int(nHTTPResponseCode)], True)
				
		
	def _header(self, strHeader, bReplace = True):
		"""WARNING: Changed this part"""
		_bHTTPMode = "REQUEST_METHOD" in os.environ and \
					os.environ["REQUEST_METHOD"] in ("GET", "POST", "PUT", "HEAD", "DELETE", "OPTIONS", "TRACE", "CONNECT")


		"""WARNING: header function"""
		if (_bHTTPMode):
			header(strHeader, bReplace)
		

	JSONRPC_VERSION = "2.0"


	"""WARNING: Removed & reference"""
	def validateDataTypes(self, arrParamsDetails, arrParams):
		if (self.bValidateTypes == False):
			return

		idx = -1
		for i in arrParamsDetails:
			idx += 1
			strParamName = i["param_name"]

			if (i not in arrParams):
				if (len(i["param_default_value_json"]) == 0):
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + \
											"] is mandatory and doesn't have a default value.", JSONRPC_Exception.INVALID_PARAMS)
				else:
					return

			if ((arrParams[idx] == None) and (i["param_default_value_json"] != None)):
				raise JSONRPC_Exception("Parameter " + strParamName + " cannot be NULL.", JSONRPC_Exception.INVALID_PARAMS)
			
			if (arrParams[idx] == None):
				continue

			"""WARNING: Check switch synthax"""
			"""WARNING: Check if param_type is string or actual type"""
			if (i["param_type"] == "integer"):
				if (isinstance(arrParams[idx], int)):
					"""WARNING: prolly not break here"""
					continue

				"""WARNING: Check if casts are correct"""
				if (not isinstance(arrParams[idx], basestring) or basestring(int(arrParams[idx])) != basestring(arrParams[idx])):
					"""WARNING: CHeck json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + \
						"], must be an integer (Number JSON type with no decimals), " + type(arrParams[idx]) + " given.", JSONRPC_Exception.INVALID_PARAMS)
					
				arrParams[idx] = int(arrParams[idx])
				continue

			elif (i["param_type"] == "float"):
				if (isinstance(arrParams[idx], float) or isinstance(arrParams[idx], int)):
					"""WARNING: prolly not break here"""
					continue
				
				"""WARNING: Check casts"""
				if ((not isinstance(arrParams[idx], basestring)) or (basestring(float(arrParams[idx])) != arrParams[idx])):
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + "], must be a Number., " \
											+ type(arrParams[idx]) + " given.", JSONRPC_Exception.INVALID_PARAMS)

				arrParams[idx] = float(arrParams[idx])
				continue
				
			elif (i["param_type"] == "boolean"):
				if (isinstance(arrParams[idx], bool)):
					"""WARNING: prolly not a break here"""
					continue

				if (isinstance(arrParams[idx], list) or isinstance(arrParams[idx], object)):
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + "], must be Boolean, " \
											+ type(arrParams[idx]) + " given.", JSONRPC_Exception.INVALID_PARAMS)

				if (basestring(arrParams[idx]) == "0"):
					arrParams[idx] = False
				elif (basestring(arrParams[idx]) == "1"):
					arrParams[idx] = True
				else:
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + "], must be Boolean, " \
											+ type(arrParams[idx]) + " given.", JSONRPC_Exception.INVALID_PARAMS)
				continue
			elif (i["param_type"] == "array"):
				if (not isinstance(arrParams[idx], list)):
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + "], must be an Array, " \
											+ type(arrParams[idx]) + " given.", JSONRPC_Exception.INVALID_PARAMS)
				elif (isinstance(arrParams[idx], dict)):
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + \
											"], must be an Array, Object (key:value collection) given.", JSONRPC_Exception.INVALID_PARAMS)

				continue


			elif (i["param_type"] == "object"):
				if (not isinstance(arrParams[idx], list)):
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + "], must be an Object, " \
											+ type(arrParams[idx]) + " given.", JSONRPC_Exception.INVALID_PARAMS)
				elif (not isinstance(arrParams[idx], dict) and (not isinstance(arrParams[idx], object)) \
						and (not isinstance(arrParams[idx], list)) and (len(arrParams[idx]) == 0)):
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + "], must be an Object (key:value collection), " 
											+ type(arrParams[idx]) + " given.", JSONRPC_Exception.INVALID_PARAMS)

				continue


			elif (i["param_type"] == "string"):
				if (isinstance(arrParams[idx], basestring)):
					"""WARNING: prolly shouldn't be a break here"""
					continue

				if ((not isinstance(arrParams[idx], basestring)) and (not isinstance(arrParams[idx], int))):
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + idx + " [" + json.dumps(strParamName) + "], must be a String, " \
											+ json.dumps(arrParams[idx]) + " given.", JSONRPC_Exception.INVALID_PARAMS)
				arrParams[idx] = basestring(arrParams[idx])
				continue
			elif (i["param_type"] == "mixed"):
				"""WARNING: Change this. There is no mixed type in python"""
				"""WARNING: prolly shouldn't be a break here"""
				continue
			else:
				"""WARNING: Check json.dumps"""
				raise JSONRPC_Exception("Unhandled type " + json.dumps(arrParamsDetails[i]["param_type"]) + ".", JSONRPC_Exception.INVALID_PARAMS)


	"""WARNING: Removed & reference"""
	def returnDataTypeValidation(self, strMethodName, strExpectedDataType, mxResult):
		if (self.bValidateTypes == False):
			return
			
		"""WARNING: Check mixed type. It does not exist in python"""
		if (strExpectedDataType == "mixed"):
			return
			
		if (strExpectedDataType == "unknown"):
			return
			
		if (isinstance(mxResult, list) and strExpectedDataType == "object" and \
			(isinstance(mxResult, dict) or len(mxResult) == 0)):
			mxResult = object(mxResult)
		elif (isinstance(mxResult, int) and strExpectedDataType == "float"):
			mxResult = float(mxResult)
						
		strReturnType = type(mxResult)
			
		if (strReturnType == "double"):
			strReturnType = "float"
			
		if (strReturnType.lower() != strExpectedDataType.lower()):
			"""WARNING: Check json.dumps"""
			raise JSONRPC_Exception("Method " + json.dumps(strMethodName) + " declared return type is " + strExpectedDataType + \
									", and it attempted returning " + strReturnType + ". The function call may have succeeded as it attempted to return.", \
									JSONRPC_Exception.INVALID_RETURN_TYPE)


	"""WARNING: Eliminated & reference"""
	def namedParamsTranslationAndValidation(self, arrParamsDetails, arrParams, strMethodName):
		#Count number of mandatory parameters
		nMandatoryParams = 0
		for arrParam in arrParamsDetails: 
			if (len(arrParam["param_default_value_json"]) == 0):
				nMandatoryParams = nMandatoryParams + 1
			else:
				break

		if ((len(arrParams) > 0) and isinstance(arrParams, dict)):
			#Named parameters
			arrNewParams = []

			for arrParamProperties in arrParamsDetails:
				"""WARNING: is arr really array? Or is it dict/tuple? """
				if (arrParamProperties["param_name"] in arrParams):
					"""WARNING: Error prone"""
					arrNewParams.append(arrParams[arrParamProperties["param_name"]])
				elif (len(arrParamProperties["param_default_value_json"]) > 0):
					arrNewParams.append(arrParamProperties["param_default_value_json"])
				else:
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Missing mandatory method parameter " + json.dumps(arrParamProperties["param_name"]) + " for method " + \
											 json.dumps(strMethodName) + ".", JSONRPC_Exception.INVALID_PARAMS)
				
				"""WARNING: Check unset or deletion of value from array"""
				del arrParams[arrParamProperties["param_name"]]

			if (len(arrParams) > 0):
				"""WARNING: Check json.dumps"""
				raise JSONRPC_Exception("Too many parameters given to method " + json.dumps(strMethodName) + ". Extra parameters: " + \
										 json.dumps(arrParams.keys()) + ".", JSONRPC_Exception.INVALID_PARAMS)
					
			arrParams = arrNewParams

		else: 
			#Unnamed params
			if (len(arrParams) > len(arrParamsDetails)):
				raise JSONRPC_Exception("Expected param(s): " + self.getParamNamesAsString(arrParamsDetails) + "." + \
										" Too many parameters for method " + strMethodName + ".", JSONRPC_Exception.INVALID_PARAMS)
					
			if (len(arrParams) < nMandatoryParams):
				raise JSONRPC_Exception("Expected param(s): " + self.getParamNamesAsString(arrParamsDetails) + "." + \
										" Missing " + (nMandatoryParams - len(arrParams)) + " required parameter(s) for method " + \
										strMethodName + ".", JSONRPC_Exception.INVALID_PARAMS)

	def getParamNamesAsString(self, arrParamsDetails):
		strParamNames = ""

		for param in self.getParamNames(arrParamsDetails):
			strParamNames = strParamNames + param + ", "
			
		strParamNames = strParamNames[:len(strParamNames)-2]
		return strParamNames


	def getParamNames(self, arrParamsDetails):
		arrParamsName = []

		if (len(arrParamsDetails) > 0):
			for value in arrParamsDetails: 
				if (len(value["param_default_value_json"]) > 0):
					arrParamsName.append(value["param_name"] + "=" + value["param_default_value_json"])
				else:
					arrParamsName.append(value["param_name"])
		return arrParamsName
		
		
	"""
	* Outputs HTTP cross site origin headers.
	* This function never returns if during an HTTP OPTIONS request, as it will exit(0) at the end.
	* @param array arrAllowedDomains.
	* @param array arrAllowedHeaders = []. Headers in addition to those allowed by default ["origin", "content-type", "accept"].
	* @param bool bAllowAllURLs = False.
	* @return None.
	"""
	def CORS_headers(self, arrAllowedDomains, arrAllowedHeaders = [], bAllowAllURLs = False):
		"""This sends the headers back to the origin. It may not be correct."""
		# Note .htaccess trick: 
		# SetEnvIf Origin "^http(s)?://(.+\.)?(localhost|stackoverflow.com|example1.com)(:[0-9]+)?$" origin_is=$0
		# Header always set Access-Control-Allow-Origin %{origin_is}e env=origin_is
			
			
		strAllowedOrigin = None

			
		arrAllowedHeaders = arrAllowedHeaders + ["origin", "content-type", "accept", "authorization"]
		
		if (os.environ["HTTP_ORIGIN"] != None):
			strHost = urlparse(os.environ["HTTP_ORIGIN"]).hostname

			if (strHost in arrAllowedDomains):
				strAllowedOrigin = os.environ["HTTP_ORIGIN"]

		#if(is_null($strAllowedOrigin) and count($arrAllowedDomains))
			#$strAllowedOrigin="https://".implode(", https://", $arrAllowedDomains).", http://".implode(", http://", $arrAllowedDomains);
			
		if (bAllowAllURLs):			
			conn = httplib.HTTPConnection(strAllowedOrigin)
			conn.putheader("Access-Control-Allow-Origin", True)
		elif (strAllowedOrigin != None):
			conn = httplib.HTTPConnection(strAllowedOrigin)
			conn.putheader("Access-Control-Allow-Origin", strAllowedOrigin)
		elif os.environ["REQUEST_METHOD"] != None and os.environ["REQUEST_METHOD"] == "OPTIONS":
			exit(0)

		conn.putheader("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT")
		conn.putheader("Access-Control-Max-Age", 86400)
		conn.putheader("Access-Control-Allow-Headers", ", ".join(arrAllowedHeaders))
		conn.puteader("Access-Control-Allow-Credentials", True)

		if os.environ["REQUEST_METHOD"] != None and os.environ["REQUEST_METHOD"] == "OPTIONS":
			exit(0)