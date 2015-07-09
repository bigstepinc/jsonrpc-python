"""
 * When using multiple plugins, it is preferable for the Reflection plugin to be added first to make necessary translations in time.
"""
"""TODO: Imports"""
import inspect
from ServerFilterBase import JSONRPC_ServerFilterBase
import Server

class ReflectionPlugin(JSONRPC_ServerFilterBase):
	
	"""
	 * @var array
	"""
	_dictJSONRPCReflectionFunctions = {"rpc.functions" : "JSONRPC\Filters\Server\ReflectionPlugin::functions",
									"rpc.reflectionFunction" : "JSONRPC\Filters\Server\ReflectionPlugin::reflectionFunction",
									"rpc.reflectionFunctions" : "JSONRPC\Filters\Server\ReflectionPlugin::reflectionFunctions",
									"rpc.allowedCrossSiteXHRSubdomains" : "JSONRPC\Filters\Server\ReflectionPlugin::allowedCrossSiteXHRSubdomains"}

		
	"""
	 * @var bool
	"""
	_bCodeComments = True

		
	"""
	 * @var array
	"""
	_arrAllowedCrossSiteXHRSubdomains = []

		
	"""
	 * @var array
	"""
	_dictTagsParsers = {"@return" : "_reflectionFunctionReturn", "@errors" : "_reflectionFunctionErrors"}
		
		
	"""TODO: Check comments"""
	"""
	 * @var \JSONRPC\Server
	"""
	_server = None
		

	"""
	 * @override
	 * 
	 * @param bool $bCodeComments=true
	 * @param array $arrAllowedCrossSiteXHRSubdomains=array()
	"""
	"""WARNING: Check this [] gotcha. May be necessary to put None instead"""
	def __init__(self, bCodeComments = True, arrAllowedCrossSiteXHRSubdomains = []):
		assert(isinstance(bCodeComments, bool))
		_bCodeComments = bCodeComments
		self._arrAllowedCrossSiteXHRSubdomains = arrAllowedCrossSiteXHRSubdomains


	"""
	 * Exported for RPC with the name: rpc.allowedCrossSiteXHRSubdomains.
	 * 
	 * Returns a string array with allowed XHR subdomain names.
	 * 
	 * @return array
	"""
	def allowedCrossSiteXHRSubdomains(self):
		return self._arrAllowedCrossSiteXHRSubdomains
		

	"""
	 * @param \JSONRPC\Server $server
	 * 
	 * @return None
	"""
	def setServerInstance(self, server): 
		self._server = server


		
	"""
	 * @override
	 * 
	 * @param string strFunctionName
	 * 
	 * @return bool
	"""
	def isFunctionNameAllowed(self, strFunctionName):
		return strFunctionName in _dictJSONRPCReflectionFunctions


	"""
	 * @override
	"""
	"""WARNING: Removed & reference"""
	def beforeJSONDecode(self, strJSONRequest):
		if (not self._server.bAuthenticated or not self._server.bAuthorized):
			"""TODO: Fix namespaces"""
			print "From reflection with love " + strJSONRequest
			arrRequest = Server.JSONRPC_Server.decodeJSONSafely(strJSONRequest, True)
			if (self.isFunctionNameAllowed(arrRequest["method"])):
				self._server.bAuthenticated = True
				self._server.bAuthorized = self._server.bAuthenticated

	"""
	 * @override
	"""
	"""WARNING: Removed & reference"""
	def afterJSONDecode(self, arrRequest):
		if (not self._server.bAuthenticated or not self._server.bAuthorized):
			if (self.isFunctionNameAllowed(arrRequest["method"])):
				self._server.bAuthenticated = True
				self._server.bAuthorized = self._server.bAuthenticated

	"""
	 * @override
	"""
	"""WARNING: Removed & reference"""
	def callFunction(self, strFunctionName, arrParams, bCalled):
		if (self.isFunctionNameAllowed(strFunctionName)):
			bCalled = True
			"""WARNING: Check mxResult"""
			"""TODO: call_user_func_array"""
			mxResult = _dictJSONRPCReflectionFunctions[strFunctionName](arrParams)
		else:
			mxResult = None

		return mxResult

		
	"""
	 * Exported for RPC with the name: rpc.functions.
	 * 
	 * Returns exported function names.
	 * 
	 * @return array
	"""
	def functions(self):
		return self._server.arrAllowedFunctionCalls
		

	"""
	 * Exported for RPC with the name: rpc.reflectionFunction.
	 * 
	 * This function is exposed through RPC as authorized and authenticated for any caller.
	 * It validates on its own if the requested Reflection is for an exposed function.
     * 
	 * strFunctionName us an unresolved function name, as seen on the RPC.
	 * 
     * 
	 * @param string strFunctionName
     * 
     * @return array
	"""
	def reflectionFunction(self, strFunctionName):
		"""TODO: Check if this is correct"""
		self._server.assertFunctionNameAllowed(strFunctionName)


		for objFilterPlugin in self._server.arrFilterPlugins:
			objFilterPlugin.resolveFunctionName(strFunctionName)

		"""TODO: Check if this works"""
		if (function_exists(strFunctionName)):
			reflector = ReflectionFunction(strFunctionName)

		elif (hasattr(strFunctionName, __call__) and isinstance(strFunctionName, basestring)): 
			"""Skipping callable array with instance and method"""
			"""TODO: Find out what explode does"""
			arrClassAndStaticMethod = strFunctionName.split("::")
			reflector = ReflectionMethod(arrClassAndStaticMethod[0], arrClassAndStaticMethod[1])
		else:
			"""Replaced callable because it is a keyword"""
			fCallable = self._server.functionNameToCallableArray(strFunctionName)
			"""TODO"""
			#reflector = ReflectionMethod(type("""Class instance""" fCallable[0]), """Method name""" fCallable[1])


		dictFunctionReflection = {"function_name" : strFunctionName, "function_return_type" : "unknown", \
								"function_documentation_comment": reflector.getDocComment(), "function_params" : []}

		"""TODO: Make this static?"""
		"""TODO: This is subject to change according to python data types and structures"""
		dictTypeMnemonicsToTypes = {"n" : "integer", "f" : "float", "str" : "string", "arr" : "array", \
									"b" : "boolean", "obj" : "object", "mx" : "mixed"}

		arrReflectionParameters = reflector.getParameters()
		for reflectionParameter in arrReflectionParameters:
			"""TODO: Replace str_replace"""
			dictParam = {"param_name" : str_replace(array("\$", "&"), array("", ""), reflectionParameter.getName()),
						"param_is_passed_by_reference" : reflectionParameter.isPassedByReference()}

			dictParam["param_type"] = "unknown"
			for strMnemonic, strType in dictTypeMnemonicsToTypes:
				if (dictParam["param_name"][:len(strMnemonic)] == strMnemonic):
					"""TODO: ctype"""
					"""
					and ctype_upper(substr(dictParam["param_name"], len(strMnemonic), 1))):
					"""

					dictParam["param_type"] = strType
					break

			if (reflectionParameter.isDefaultValueAvailable()):
				"""TODO: check if it's json dumps or loads"""
				dictParam["param_default_value_json"] = json.dumps(reflectionParameter.getDefaultValue())
				dictParam["param_default_value_constant_name"] = self.reflectionConstantName(reflectionParameter.getName(), \
																							dictFunctionReflection["function_documentation_comment"])
			else:
				dictParam["param_default_value_json"] = ""
				dictParam["param_default_value_constant_name"] = ""

			dictFunctionReflection["function_params"].append(dictParam)

		for strTag, fnParser in self._arrTagsParsers:
			fnParser(arrFunctionReflection, strTag)

		if (not _bCodeComments):
			"""WARNING: Not sure if value needs to be deleted or set to None"""
			arrFunctionReflection["function_documentation_comment"] = None

		return dictFunctionReflection
		

	"""WARNING: This was inside the next function"""
	"""
	dictTypeMnemonicsToTypes = array(
			"n"=>"integer",
			"f"=>"float",
			"str"=>"string",
			"arr"=>"array",
			"b"=>"boolean",
			"obj"=>"object",
			"mx"=>"mixed",
		);

	dictPHPTypesToTypes=array(
		"int"=>"integer",
		"double"=>"float",
		"float"=>"float",
		"string"=>"string",
		"array"=>"array",
		"bool"=>"boolean",
		"object"=>"object",
		"mixed"=>"mixed",
		"null"=>"null",
		"none"=>"unknown",
	);
	"""

	"""
	 * @param array arrFunctionReflection 
	 * @param string strTag 
	 * 
	 * @return None
	 * 
	 * @throws \JSONRPC\Exception 
	 * @throws \Exception 
	"""
	"""WARNING: Removed & reference"""
	def _reflectionFunctionReturn(self, arrFunctionReflection, strTag):

		"""TODO: strpos"""
		if (strpos(dictFunctionReflection["function_documentation_comment"], strTag) != False):
			"""TODO: preg_replace"""
			strFunctionDocumentationComment = preg_replace('!\s+!', ' ', dictFunctionReflection["function_documentation_comment"])
		
			"""TODO: preg_match"""
			preg_match('/(?<=(@return ))(\S\w*)/', strFunctionDocumentationComment, arrReturnParts)
			
			"""TODO: check type of arrReturnParts"""
			if (len(arrReturnParts) == 0):
				"""Check if json.loads or dumps"""
				raise JSONRPC_Exception("Cannot read @return property from function " + json.dumps(dictFunctionReflection["function_name"]))
				
			# for compatibility 
			# translate replaces all dots (.) with nothing, and then strip removes the trailing and beginning whitespaces 
			strReturnType = arrReturnParts[0].translate(None, ".").strip()

			"""TODO: Not sure if this should be set to None or deleted"""
			arrReturnParts = None
				
			if (strReturnType in dictTypeMnemonicsToTypes):
				dictFunctionReflection["function_return_type"] = strReturnType
			elif (dictPHPTypesToTypes.get(strReturnType.lower()) != None):
				dictFunctionReflection["function_return_type"] = dictPHPTypesToTypes[strReturnType.lower()]
			else:
				if (self._server == None):
					raise Exception("Please use .setServerInstance().")
					
				if (self._server.bValidateTypes):
					raise JSONRPC_Exception("Invalid @return property type " + json.dumps(strReturnType) + " from " + dictFunctionReflection["function_name"])
				else:
					"""TODO: Modify mixed"""
					dictFunctionReflection["function_return_type"] = "mixed";


	"""
	 * @param dictionary dictFunctionReflection 
	 * @param string strTag 
	 * 
	 * @return None
	 * 
	 * @throws JSONRPC_Exception 
	"""
	"""WARNING: parameters may be not needed"""
	def _reflectionFunctionErrors(self, dictFunctionReflection, strTag):
		"""TODO: strpos"""
		nErrorsPosition = strpos(dictFunctionReflection["function_documentation_comment"], strTag)
		if (nErrorsPosition != False):
			"""TODO: preg_split"""
			arrParts = preg_split("/[\.\r\n]+/", dictFunctionReflection["function_documentation_comment"][nErrorsPosition+len("@errors ")])
			if (len(arrParts[0])):
				"""TODO: preg_split"""
				dictFunctionReflection["function_error_constants"] = preg_split("/[\s,]+/", arrParts[0])
			else:
				raise JSONRPC_Exception("@errors property from " + dictFunctionReflection["function_name"] + " should be removed because it contains no errors.")
		else:
			dictFunctionReflection["function_error_constants"] = []

		
	"""
	 * Exported for RPC with the name: rpc.reflectionFunctions.
	 * 
	 * @param string arrFunctionNames 
	 * 
	 * @return array
	"""
	def reflectionFunctions(self, arrFunctionNames):
		dictReflectionFunctions = []

		for strFunctionName in arrFunctionNames:
			dictReflectionFunctions[strFunctionName] = self.reflectionFunction(strFunctionName)
		return dictReflectionFunctions

		
	"""
	 * Returns the name of the constant given as a default parameter.
	 * In order to find the name of the constant it must appear in the doc comment of the function in the following format:
	 *  "* @param .... parameterName=CONSTANT_NAME...."
	 *  
	 * Returns the name of the constant or an empty string if not found.
	 *  
	 * @param int strReflectionParameterName
	 * @param string strDocComment
	 * 
	 * @return string
	"""
	def reflectionConstantName(self, strReflectionParameterName, strDocComment):
		arrDocCommentLines = strDocComment.split('\n')
			
		for strDocCommentLine in arrDocCommentLines:
			arrRegexMatches = []

			"""TODO: preg_match"""
			if (preg_match("/^[\w\W]*@param[\w\W]*" + strReflectionParameterName  + "=/", strDocCommentLine, arrRegexMatches)):
				nOffset = len(arrRegexMatches[0])
				"""TODO: preg_match"""
				if (preg_match("/[A-Z]{1,1}[A-Z0-9_]+/", strDocCommentLine, arrRegexMatches, 0, nOffset)):
					if (arrRegexMatches[0] != "NULL"):
						return arrRegexMatches[0]

				return ""
			
		return ""