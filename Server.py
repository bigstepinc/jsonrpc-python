import request
import os
import json
from JSONRPC_Exception import JSONRPC_Exception
class JSONRPC_Server(object):
	
	def __init__(self):
	{
	}

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
	arrExceptionTypesForMessages = ["JSONRPC\\Exception"]
		
		
	"""
	* Debug aid.
	* If true, it overrides ::arrExceptionTypesForMessages and all exception messages are allowed.
	* Should not be used on production servers.
	* @var bool
	"""
	bDebugAllowAllExceptionMessages = False
		
		
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
	strErrorLogFilePath = ""
		
		
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
		

	"""
	* As returned by \JSONRPC\Filters\Server\ReflectionPlugin::reflectionFunction().
	* 
	* @var array
	"""
	arrFunctionReflection = None
		
		
	"""
	* Associative array with class names as keys and \JSONRPC\MethodsMapper instances as values.
	* 
	* @var array
	"""
	arrMethodsMappers = []
		
		
	def processRequest(self, strJSONRequest = None):
		self._exitWithResponse(self.processRequestAndReturn(strJSONRequest))

		
		
	def processRequestAndReturn(self, strJSONRequest = None):
		objReflectionPlugin = ReflectionPlugin()
		objReflectionPlugin.setServerInstance(self);

		"""TODO"""
		"""Check import.request"""
		"""
		if(isset($_SERVER["REQUEST_METHOD"]) && !in_array($_SERVER["REQUEST_METHOD"], array("GET", "POST", "PUT", "OPTIONS")))
		{
				echo "HTTP request method ".$_SERVER["REQUEST_METHOD"]." ignored.";
				exit(0);
		}
		"""

		mxRequestID = None
		try:
			"""TODO
			"//php://input must be read here only for normal HTTP POST JSON-RPC requests.
			if (strJSONRequest == None && (!isset($_SERVER["REQUEST_METHOD"]) || $_SERVER["REQUEST_METHOD"]=="POST"))
					$strJSONRequest=file_get_contents("php://input");
			"""
				
			for plugin in self.arrFilterPlugins: 
				plugin.beforeJSONDecode(strJSONRequest)

				
			if (len(strJSONRequest.strip()) != 0):
				raise JSONRPC_Exception("Invalid request. Empty input. Was expecting a POST request of a JSON.", JSONRPC_Exception.PARSE_ERROR);
				
			"""TODO"""
			#dictRequest = static::decodeJSONSafely($strJSONRequest);
				
			# May have a problem at indexation in dictionaries	
			if (dictRequest[0] != None)
				raise JSONRPC_Exception("JSON-RPC batch requests are not supported by this server.", JSONRPC_Exception.INVALID_REQUEST);
					

			if ((dictRequest["method"] != None) && isinstance(dictRequest["method"], basestring) && \
							 (len(dictRequest["method"].strip()) != 0) && ("params" in dictRequest)):
				self.arrFunctionReflection = None

				try:
					self.arrFunctionReflection = objReflectionPlugin.reflectionFunction(dictRequest["method"])
				except Exception as e: 
				    #Ignoring because the reflection is expected to sometimes fail here.
                    #The reflection will be retried later where it is not expected to fail.
                    #One of these tries must succeed to obtain the functions reflection object.
				
				if(self.arrFunctionReflection != None):
					self.namedParamsTranslationAndValidation(self.arrFunctionReflection["function_params"], dictRequest["params"], dictRequest["method"])
					self.validateDataTypes(self.arrFunctionReflection["function_params"], dictRequest["params"])
				
			for plugin in self.arrFilterPlugins: 
				plugin.afterJSONDecode(dictRequest)
			

			#A String containing the name of the method to be invoked. 
			#Method names that begin with the word rpc followed by a period character (U+002E or ASCII 46)
			#are reserved for rpc-internal methods and extensions and MUST NOT be used for anything else.
			if (
				(dictRequest["method"] != None) \
				|| (not isintstance(dictRequest["method"], basestring)) \
				|| (len(dictRequest["method"].strip()) != 0)
			):
				raise JSONRPC_Exception("The \"method\" key must be a string with a function name.", JSONRPC_Exception.INVALID_REQUEST)
				
				
				
			#A Structured value that holds the parameter values to be used during the invocation of the method.
			#This member MAY be omitted.
			if (not "params" in dictRequest):
				dictRequest["params"] = []
				
			if (not isinstance(dictRequest["params"], list)):
				raise JSONRPC_Exception("The \"params\" key must be an array.", JSONRPC_Exception.INVALID_REQUEST);


				
			#second if condition may be incorrect
			if (hasattr(dictRequest["method"], '__call__') || (dictRequest["method"] != None)):
				self.arrFunctionReflection = objReflectionPlugin.reflectionFunction(dictRequest["method"])
				self.namedParamsTranslationAndValidation(self.arrFunctionReflection["function_params"], dictRequest["params"], dictRequest["method"])
				self.validateDataTypes(self.arrFunctionReflection["function_params"], dictRequest["params"])
			

			"""TODO"""
			"""if (
                isset($_SERVER["REQUEST_METHOD"])
				&& $_SERVER["REQUEST_METHOD"]==="OPTIONS" 
				&& !in_array($arrRequest["method"], $this->arrAllowedFunctionCallsFor_HTTP_OPTIONS)
			)
			{
				echo "HTTP request method ".$_SERVER["REQUEST_METHOD"]." ignored.";
				exit(0);
			}
			"""


			#An identifier established by the Client that MUST contain a String, Number, or NULL value if included. 
			#If it is not included it is assumed to be a notification. 
			#The value SHOULD normally not be Null and Numbers SHOULD NOT contain fractional parts.
			self.bNotificationMode = not "id" in dictRequest
				
			if ((not self.bNotificationMode) && (not ininstance(dictRequest["id"], int)) && (not dictRequest["id"] != None)):
				raise JSONRPC_Exception("The \"id\" key must be an integer, a null or be omitted for Notification requests.", JSONRPC_Exception::INVALID_REQUEST)
				
			if (not self.bNotificationMode):
				mxRequestID = dictRequest["id"]
				
				
				
			#A String specifying the version of the JSON-RPC protocol. MUST be exactly "2.0".
			if ((not dictRequest["jsonrpc"] == None) || (dictRequest["jsonrpc"] != self.JSONRPC_VERSION)):
				raise JSONRPC_Exception("The \"jsonrpc\" version must be equal to ".self.JSONRPC_VERSION, JSONRPC_Exception.INVALID_REQUEST)
				
				
				
			self.assertFunctionNameAllowed(dictRequest["method"])
				
				
				
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
				
			if ((self.arrFunctionReflection != None) && count(self.arrFunctionReflection) != 0):
				self.returnDataTypeValidation(dictRequest["method"], self.arrFunctionReflection["function_return_type"], dictResponse["result"])

			if (self.nHTTPResponseCode == 0):
				if (self.bNotificationMode == True):
					self.nHTTPResponseCode = self.HTTP_204_NO_CONTENT
				else
					self.nHTTPResponseCode = self.HTTP_200_OK
			
		
		except Exception as exc:
			try:
				self._log_exception(exc)
					
				#Gives a chance to log the original Exception and/or throw another "translated" Exception.
				#If nothing is thrown inside exceptionCatch, this catch block will rethrow the original Exception anyway.
				for plugin in self.arrFilterPlugins:
					plugin.exceptionCatch(exc)
				raise exc

			except Exception as exc:
				dictResponse = self._exceptionToJSONResponse(exc)
			
			
		dictResponse["jsonrpc"] = self.JSONRPC_VERSION
		if (not self.bNotificationMode):
			dictResponse["id"] = mxRequestID			
            
    	try:
            for plugin in self.arrFilterPlugins:
       			plugin.response(dictResponse)

        except Exception as exc:
            this._log_exception(exc)
                
            if (dictResponse["error"] == None):
                dictResponse = self._exceptionToJSONResponse(exc)
            
			
		return dictResponse
		
        


    """
    * Will affect the HTTP status.
    """
    def _exceptionToJSONResponse(self, Exception exc):
        strExceptionClass = exc.__class__.__name__
        """TODO"""
        """Trim the class name for slashes"""
        """
		while (substr(strExceptionClass, 0, 1)=="\\"):
		{
			$strExceptionClass=substr($strExceptionClass, 1);
		}
		"""	
    		
		if (strExceptionClass in self.arrExceptionTypesForMessages):
			strMessage = exc.getMessage()
		
		"""TODO"""
		"""Check exception functions"""
		else if (self.bDebugAllowAllExceptionMessages == True):
			strMessage =
				"[Internal error: " + strExceptionClass + "] " + exc.getMessage() + " "
				+ os.linesep + exc.getFile() + "#" + exc.getLine() + " "
				+ os.linesep + exc.getTraceAsString()
		else:
			strMessage = "Internal error."
				
		if (strExceptionClass in self.arrExceptionTypesForCodes):
			nCode = (int)exc.getCode()
		else
			nCode = 0
						
		if (self.nHTTPResponseCode == 0):
			if (nCode in [JSONRPC_Exception.NOT_AUTHENTICATED, JSONRPC_Exception.NOT_AUTHORIZED]):
				self.nHTTPResponseCode = self.HTTP_403_FORBIDDEN
			else:
				self.nHTTPResponseCode = self.HTTP_500_INTERNAL_SERVER_ERROR
			
		dictResponse["error"] = ["message" : strMessage, "code" :$nCode]
            
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
			print json_encode(dictResponse)
			
		if (self.nHTTPResponseCode in [self.HTTP_200_OK, self.HTTP_204_NO_CONTENT]):
			sys.exit(0)
		
		sys.exit(1)

		
	def callFunction(self, strFunctionName, dictParams):
		"""TODO"""
		"""Find similar function for python"""
		#ignore_user_abort(true);
			
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
			if(strFunctionName.__call__ != None):
				fcallable = self.functionNameToCallableArray(strFunctionName)
				"""TODO"""
				"""Find equivalent for call_user_func_array in python"""
				mxResult = call_user_func_array(fcallable, self.array_make_references(dictParams))
			else:
				mxResult = call_user_func_array(strFunctionName, self.array_make_references(dictParams))
				"""END_TODO"""
				
		return mxResult
		
		
	"""
	plugin is of type JSONRPC_ServerFilterBase
	"""
	def addFilterPlugin(self, plugin):
		for pluginExisting in self.arrFilterPlugins:
			if (pluginExisting.__class__ == plugin.__class__):
				return
		plugin.setServerInstance(self)
		"""???"""
		self.arrFilterPlugins[] = plugin
		
		
	"""
	plugin is of type JSONRPC_ServerFilterBase
	"""
	def removeFilterPlugin(self, plugin):
		nIndex = None
		for nIndexExisting in self.arrFilterPlugins:
			if (self.arrFilterPlugins[nIndexExisting].__class__ == plugin.__class__):
				nIndex = nIndexExisting
				break

		if (isinstance(nIndex, int) == False):
			raise Exception("Failed to remove filter plugin object, maybe plugin is not registered.")
			
		"""WARNING: Splice attempt"""
		self.arrFilterPlugins = self.arrFilterPlugins[:nIndex]
		
		
	"""
	methodsMapper is of type JSONRPC_MethodsMapper
	"""
	def addMethodsMapper(self, methodsMapper):
		for methodsMapperExisting in self.arrMethodsMappers:
			if (methodsMapperExisting == methodsMapper):
				return

		self.arrMethodsMappers[methodsMapper.__class__.instanceWithAPIMethods()] = methodsMapper
		
		
	def removeMethodsMapper(self, methodsMapper):			
		strInstanceAPIClassNameExisting = methodsMapper.instanceWithAPIMethods().__class__
			
		if (strInstanceAPIClassNameExisting in self.arrMethodsMappers):
			self.arrMethodsMappers[strInstanceAPIClassNameExisting] = None;
		else:
			raise Exception("Failed to remove methodsMapper object.")

		
	def methodsMappers(self):
		return self.arrMethodsMappers
		
		
	"""
	 * @param string strFunctionName
	 * 
	 * @return callable
	"""
	def functionNameToCallableArray(self, strFunctionName):
		for methodsMapper in self.methodsMappers():
			if (strFunctionName in methodsMapper.arrAPIFunctionsNamesToMethodsNames()):
				# Returning callable "type".
				return [
					/*Class instance*/ 0 : methodsMapper.instanceWithAPIMethods(), \
					/*Method name*/ 1 : methodsMapper.arrAPIFunctionsNamesToMethodsNames()[strFunctionName] \
					]
			
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
			if (bFunctionNameAllowed = True):
				break

		if ((bFunctionNameAllowed == False) && (not strFunctionName in self.arrAllowedFunctionCalls)):
			self.nHTTPResponseCode = self.HTTP_403_FORBIDDEN
			raise JSONRPC_Exception("The function \"" + $strFunctionName + "\" is not exported and/or does not exist.", JSONRPC_Exception.METHOD_NOT_FOUND)
		
		
	"""
	* Safely decode JSON strings, because json_decode() does not throw errors.
	* @param string strJSON.
	* @param bool bAssoc.
	* @return mixed.
	* @throws JSONRPC_Exception.
	"""
	@staticmethod
	def decodeJSONSafely(self, strJSON, bAssoc = True):
		if (len(strJSON.strip()) == 0):
			"""TODO"""
			#raise PHorse\Utils\JSONException("Cannot run json_decode() on empty string.", \JSONRPC\Exception::PARSE_ERROR);
			
		if (bAssoc == True):
			mxReturn = json.loads(strJSON)[0]
		else:
			mxReturn = json.loads(strJSON)
			
		"""TODO"""
		"""Check for errors"""
		"""
		if (json_last_error()!=JSON_ERROR_NONE)
		{
			throw new \JSONRPC\Exception(
				"JSON deserialization failed. Error message: ".json_last_error_msg().PHP_EOL." RAW input: ".$strJSON, 
				\JSONRPC\Exception::PARSE_ERROR
			);
		}
		"""

		return mxReturn
		
	"""WARNING: Eliminated & reference"""
	def array_make_references(self, arrSomething):
		arrAllValuesReferencesToOriginalValues = []
		for mxKey in arrSomething:
			arrAllValuesReferencesToOriginalValues[mxKey] = arrSomething[mxKey]
		return arrAllValuesReferencesToOriginalValues
		
		
	def _log_exception(self, exception):
		try:
			if (len(self.strErrorLogFilePath) != 0):
				strClientInfo = ""
				"""TODO"""
				"""
				if (array_key_exists("REMOTE_ADDR", $_SERVER))
					strClientInfo = strClientInfo + " " + $_SERVER["REMOTE_ADDR"]
				if(array_key_exists("HTTP_USER_AGENT", $_SERVER))
					strClientInfo = strClientInfo + " " + $_SERVER["HTTP_USER_AGENT"]
				"""
					
				"""WARNING: Get exception functions"""
				try:
					arrTrace = exception.getTrace()

					"""TODO"""
					"""
					if (preg_match_all('@*RECURSION*@', print_r($arrTrace, true), $arrMatches))
						throw new \Exception("Recursive stack trace.");
					"""

					"""WARNING: Get exception functions"""
					"""WARNING: Check var_export strTrace = arrTrace"""
					strTrace = arrTrace
					strTrace = strTrace + os.linesep + "Short trace: " + os.linesep + exception.getTraceAsString()
	
				except Exception as exc:
					strTrace = exception.getTraceAsString()

				"""WARNING: Get exception functions"""
				strError =
					exception.getFile() + "#" + exception.getLine() + os.linesep + \
					"Exception type: " + exception.__class__.__name__ + os.linesep + \
					"Message: " + exception.getMessage() + os.linesep + \
					"Code: " + exception.getCode() + os.linesep + \
					strTrace + os.linesep

				"""TODO: file_exists"""
				"""
				if(!file_exists(dirname($this->strErrorLogFilePath)))
				{
					mkdir(dirname($this->strErrorLogFilePath), 0777, true);
				}
				error_log($strError, 3, $this->strErrorLogFilePath);
				"""

		except Exception as exc:
			"""WARNING: Check __FILE__ """
			"""WARNING: Check json.dumps """
			print "Failed error logging at " + __FILE__ + "#" + __LINE__
			print ", exception code " + json.dumps(exc.getCode()) + ", exception message: " + exc.getMessage() + ", stack trace: " + os.linesep
			print exc.getTraceAsString()
			print os.linesep
			print "Failed to log this line: " + os.linesep + strErrorLine
				
			sys.exit(1)
		
		
	HTTP_200_OK = 200
	HTTP_204_NO_CONTENT = 204
	HTTP_401_UNAUTHORIZED = 401
	HTTP_403_FORBIDDEN = 403
	HTTP_429_TOO_MANY_REQUESTS = 429
	HTTP_500_INTERNAL_SERVER_ERROR = 500
		
	def _http_response_code(self, nHTTPResponseCode):
		if (self.nHTTPResponseCode == 0):
			self.nHTTPResponseCode = self.HTTP_500_INTERNAL_SERVER_ERROR
		
		"""TODO: Static variables"""
		"""
		static $arrHTTPResponseCodesToText=array(
			self::HTTP_200_OK=>"OK",
			self::HTTP_204_NO_CONTENT=>"No Content",
			self::HTTP_401_UNAUTHORIZED=>"Unauthorized",
			self::HTTP_403_FORBIDDEN=>"Forbidden",
			self::HTTP_429_TOO_MANY_REQUESTS=>"Too Many Requests",
			self::HTTP_500_INTERNAL_SERVER_ERROR=>"Internal Server Error",
		);
		$this->_header("HTTP/1.1 ".(int)$nHTTPResponseCode." ".$arrHTTPResponseCodesToText[(int)$nHTTPResponseCode], /*$bReplace*/ true, $nHTTPResponseCode);
		"""		
		
	def _header(self, strHeader, bReplace = True):

		"""TODO: Static variables"""
		#static $_bHTTPMode=null;
			
		if (_bHTTPMode == None):
			"""TODO: Workaround _SERVER"""
			"""
			_bHTTPMode = (
				array_key_exists("REQUEST_METHOD", $_SERVER)
				&& in_array(
					$_SERVER["REQUEST_METHOD"], 
					array("GET", "POST", "PUT", "HEAD", "DELETE", "OPTIONS", "TRACE", "CONNECT")
				)
			);
			"""
						
		"""WARNING: header function"""
		if (_bHTTPMode):
			header(strHeader, bReplace)
		

	JSONRPC_VERSION = "2.0"


	"""WARNING: Check if list"""
	def isAssociativeArray(self, array):
		if (not isinstance(array, list)):
			return False

		#http://stackoverflow.com/a/4254008/1852030
		"""TODO: Wtf is this"""
		#return (bool)count(array_filter(array_keys($array), "is_string"));

	"""WARNING: Removed & reference"""
	def validateDataTypes(self, arrParamsDetails, arrParams):
		if (self.bValidateTypes == False):
			return
				
		for (i=0; i < len(arrParamsDetails); i = i + 1):
			strParamName = arrParamsDetails[i]["param_name"]

			if (not i in arrParams):
				if (len(arrParamsDetails[i]["param_default_value_json"]) == 0):
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + \
											"] is mandatory and doesn't have a default value.", JSONRPC_Exception.INVALID_PARAMS)
				else:
					return

			if ((arrParams[$i] == None) && (arrParamsDetails[i]["param_default_value_json"] != None)):
				raise JSONRPC_Exception("Parameter " + strParamName + " cannot be NULL.", JSONRPC_Exception.INVALID_PARAMS)
			
			"""WARNING: Check if continue exists"""
			if (arrParams[i] == None):
				continue

			"""WARNING: Check switch synthax"""
			"""TODO: switch"""
			switch (arrParamsDetails[i]["param_type"]):
				case "integer":
					if (isinstance(arrParams[i], int)):
						break

					if (
						"""WARNING: Check if casts are correct"""
						not isinstance(arrParams[i], basestring)
						|| (basestring)(int)arrParams[i] != (basestring)arrParams[i]
					):
						"""WARNING: CHeck json.dumps"""
						raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + \
							"], must be an integer (Number JSON type with no decimals), " + type(arrParams[i]) + " given.", JSONRPC_Exception.INVALID_PARAMS)
					
					arrParams[i] = (int)arrParams[i]
					break

				case "float":
					if (ininstance(arrParams[i], float) || isinstance(arrParams[i], int)):
						break
						
					"""WARNING: Check casts"""
					if ((not isinstance(arrParams[i], basestring)) || ((basestring)(float)arrParams[i] != arrParams[i])):
						"""WARNING: Check json.dumps"""
						raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + "], must be a Number., " \
												+ type(arrParams[i]) + " given.", JSONRPC_Exception.INVALID_PARAMS)

					arrParams[i] = (float)arrParams[i]
					break					
					
				case "boolean":
					if (isinstance(arrParams[i], bool)):
						break

					if (isinstance(arrParams[i], list) || isinstance(arrParams[i], object)):
						"""WARNING: Check json.dumps"""
						raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + "], must be Boolean, " \
												+ type(arrParams[i]) + " given.", JSONRPC_Exception.INVALID_PARAMS)
							
					if ((basestring)arrParams[i] == "0"):
						arrParams[i] = False
					else if ((basestring)arrParams[i] == "1"):
						arrParams[i] = True
					else:
						"""WARNING: Check json.dumps"""
						raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + "], must be Boolean, " \
												+ type(arrParams[i]) + " given.", JSONRPC_Exception.INVALID_PARAMS)

					break


				case "array":
					if (not isinstance(arrParams[i], list)):
						"""WARNING: Check json.dumps"""
						raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + "], must be an Array, " \
												+ type(arrParams[i]) + " given.", JSONRPC_Exception.INVALID_PARAMS)
					else if (self.isAssociativeArray(arrParams[i])):
						"""WARNING: Check json.dumps"""
						raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + \
												"], must be an Array, Object (key:value collection) given.", JSONRPC_Exception.INVALID_PARAMS)

					break


				case "object":
					if (not isinstance(arrParams[i], list)):
						"""WARNING: Check json.dumps"""
						raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + "], must be an Object, " \
												+ type(arrParams[i]) + " given.", JSONRPC_Exception.INVALID_PARAMS)
					else if (not self.isAssociativeArray(arrParams[i]) && (not isinstance(arrParams[i], object)) \
							&& (not isinstance(arrParams[i], list)) && (len(arrParams[i]) == 0)):
						"""WARNING: Check json.dumps"""
						raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + "], must be an Object (key:value collection), " 
												+ type(arrParams[i]) + " given.", JSONRPC_Exception.INVALID_PARAMS)

					break


				case "string":
					if (isinstance(arrParams[i], basestring)):
						break

					if ((not isinstance(arrParams[i], basestring)) && (not isinstance(arrParams[i], int))):
						"""WARNING: Check json.dumps"""
						raise JSONRPC_Exception("Parameter at index " + i + " [" + json.dumps(strParamName) + "], must be a String, " \
												+ json.dumps(arrParams[i]) + " given.", JSONRPC_Exception.INVALID_PARAMS)

					arrParams[i] = (basestring)arrParams[i]
					break;

				case "mixed":
					break


				default:
					"""WARNING: Check json.dumps"""
					raise JSONRPC_Exception("Unhandled type " + json.dumps(arrParamsDetails[i]["param_type"]) + ".", JSONRPC_Exception.INVALID_PARAMS)


	"""WARNING: Removed & reference"""
	def returnDataTypeValidation(self, strMethodName, strExpectedDataType, mxResult):
		if (self.bValidateTypes == False):
			return
			
		if (strExpectedDataType == "mixed"):
			return
			
		if (strExpectedDataType == "unknown"):
			return
			
		if (isinstance(mxResult, list) && strExpectedDataType == "object" && \
			(self.isAssociativeArray(mxResult) || len(mxResult) == 0)):
			mxResult = (object)mxResult

		else if (isinstance(mxResult, int) && strExpectedDataType == "float"):
			mxResult = (float)mxResult
						
		strReturnType = type(mxResult)
			
		if (strReturnType == "double"):
			strReturnType = "float"
			
		"""CONTINUE"""
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

		if ((len(arrParams) > 0) && self.isAssociativeArray(arrParams)):
			#Named parameteres
			arrNewParams = []

			for arrParamProperties in arrParamsDetails:
				"""WARNING: Check if array_key_exists""" 
				if (arrParamProperties["param_name"] in arrParams):
					"""WARNING: Error prone"""
					arrNewParams.append(arrParams[arrParamProperties["param_name"]])
				else if (len(arrParamProperties["param_default_value_json"]) > 0):
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
					arrParamsName[] = value["param_name"] + "=" + value["param_default_value_json"]					
				else:
					arrParamsName[] = value["param_name"]	

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
		# Note .htaccess trick: 
		# SetEnvIf Origin "^http(s)?://(.+\.)?(localhost|stackoverflow.com|example1.com)(:[0-9]+)?$" origin_is=$0
		# Header always set Access-Control-Allow-Origin %{origin_is}e env=origin_is
			
			
		strAllowedOrigin = None

			
		arrAllowedHeaders = arrAllowedHeaders + ["origin", "content-type", "accept", "authorization"]
		
		"""TODO: Php _SERVER again"""
		"""
		if (isset($_SERVER["HTTP_ORIGIN"]))
		{
			$strHost=parse_url($_SERVER["HTTP_ORIGIN"], PHP_URL_HOST);
				
			if(in_array($strHost, $arrAllowedDomains))
				$strAllowedOrigin=$_SERVER["HTTP_ORIGIN"];
		}
		"""

		#if(is_null($strAllowedOrigin) && count($arrAllowedDomains))
			#$strAllowedOrigin="https://".implode(", https://", $arrAllowedDomains).", http://".implode(", http://", $arrAllowedDomains);
			
		if (bAllowAllURLs):
			"""TODO: Header"""
			#header("Access-Control-Allow-Origin: *", true);
		else if (strAllowedOrigin != None):
			"""TODO: Header"""
			#header("Access-Control-Allow-Origin: ".$strAllowedOrigin, true);
		"""TODO: Php Server"""
		#lse if (isset($_SERVER["REQUEST_METHOD"]) && $_SERVER["REQUEST_METHOD"]=="OPTIONS")
		#exit(0);
	
		"""TODO: Header"""
		"""
		header("Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT", true);
		header("Access-Control-Max-Age: 86400", true);
		header("Access-Control-Allow-Headers: ".implode(", ", $arrAllowedHeaders), true);
		header("Access-Control-Allow-Credentials: true", true);
		"""

		"""TODO: Php Server"""
		"""
		if(isset($_SERVER["REQUEST_METHOD"]) && $_SERVER["REQUEST_METHOD"]=="OPTIONS")
			exit(0);
		"""