"""TODO: imports"""
import os.linesep
#require_once("JSONSchema/schema_manager.php");

class DataValidation(ServerFilterBase):
	_strFunctionName = None
	_schemaManager = None
	_server = None
	_dictFunctionReflection = None
	_reflectionPlugin = None

	"""TODO: check types"""
	def __init__(self, arrSchemas, objReflectionPlugin = None):
		self._schemaManager = SchemaManager(arrSchemas)
		SchemaManager.arrGlobalFlags[SchemaManager.STRICT_MODE] = SchemaManager.STRICT_MODE
		"""TODO: encapsulate this in try...except"""
		#if (!file_exists(BASE_PATH."/LOG/validation/")):
			"""TODO: mkdir"""
			mkdir(BASE_PATH."/LOG/validation/", 0777, true);

		if (objReflectionPlugin == None):
			self._reflectionPlugin = ReflectionPlugin()
		else:
			self._reflectionPlugin = objReflectionPlugin

	def setServerInstance(self, server):
		self._server = server

	"""WARNING: removed & reference"""
	def afterJSONDecode(self, arrRequest):
		self._strFunctionName = dictRequest["method"]
		if (dictRequest["method"] not in self._server.arrAllowedFunctionCalls):
			return

		objReflectionPlugin = self._reflectionPlugin
		objReflectionPlugin.setServerInstance(self._server)
		self._dictFunctionReflection = objReflectionPlugin.reflectionFunction(self._strFunctionName)

		"""WARNING: Removed & reference"""
		for (key, tupParam in dictRequest["params"]):
			dictParam = self._dictFunctionReflection["function_params"][key]
			if (Server.decodeJSONSafely(dictParam["param_default_value_json"]) == tupParam):
				continue

			if (dictParam["param_name"] in self._dictFunctionReflection["function_xparams"])):
				dictSchemaOptions = self._dictFunctionReflection["function_xparams"][dictParam["param_name"]]
				try:
					self._schemaManager.check(dictSchemaOptions["schema_name"], tupParam, dictSchemaOptions["schema_flags"])
				except Exception as exc:
					raise BSI_Exception(os.linesep + "Function (in) " + self._strFunctionName + ": " + os.linesep + exc.message, BSI_Exception.PROPERTY_IS_INVALID)



	"""
	* Should be used to update the JSONRPC_server response with additional info.
	* @param array arrJSONRPCResponse. Associative array in JSONRPC_server response.
	"""
	"""WARNING: Removed & reference"""
	def response(self, dictJSONRPCResponse):
		"""static $arrWhitelistedFunctions = array(
			"rpc.functions",
			"rpc.reflectionFunction",
			"rpc.reflectionFunctions",
			"resource_utilization_summary",
			"resource_utilization_detailed",
			"query_parser",
			//@TODO: fix and remove from whitelist.
			"server_reservation_create",
		);"""
		tupResult = dictJSONRPCResponse["result"]

		dictInitialResponse = dictJSONRPCResponse

		if (len(self._strFunctionName) != 0 && arrJSONRPCResponse.get("error") == None):
			dictFunctionReflection = self._dictFunctionReflection
			strXreturn = dictFunctionReflection["function_xreturn"]

			if (strXreturn != None):
				$exception = None
				SchemaManager.arrGlobalFlags[SchemaManager.REMOVE] = SchemaManager.REMOVE
				if (((strXreturn.find("{") != -1) && (strXreturn.find("}") != -1)) \
						|| ((strXreturn.find("[") != -1) && (strXreturn.find("]") != -1)))

					"""TODO: str_replace"""
					strXreturn = strStripReturnSchema.replace("{", "[")					
					strXreturn = strStripReturnSchema.replace("}", "]")
					strSchema = self._strFunctionNamei + "." + strStripReturnSchema
					"""TODO: wtf is this"""
					tupResult = (array)$mxResult

					strErrorMessage = ""

					for (strKey, dictResult in tupResult):
						try:
							self._schemaManager.check(strSchema, dictResult, [SchemaManager.REQUIRED_ALL, SchemaManager.IGNORE_DEFAULT, SchemaManager.IGNORE_READONLY])
					
						except Exception as exc:
							strErrorMessage += strKey + " : \n\t" + "\n\t".join(exc.message.split(os.linesep)) + os.linesep + os.linesep
				
					if (strErrorMessage != ""):
						exception = Exception(strErrorMessage)
				else:
					strSchema = self._strFunctionName + "." + strXreturn
					"""Check is is_object is an overriden function or is just the equivalent of isinstance"""
					if (SchemaManager.is_object(tupResult)):
						"""WARNING: Done cast here, but didn't do somewhere else"""
						tupResult = list(tupResult)
						
					try:
						self._schemaManager.check(strSchema, tupResult, [SchemaManager.REQUIRED_ALL, SchemaManager.IGNORE_DEFAULT, SchemaManager.IGNORE_READONLY])
					except Exception as exc:
						exception = exc

				if (exception != None):
					if (config().isProduction()):
						afc().addCallDebugNormal(
							"""TODO: Check types"""
							list(arrInitialResponse),
							"return_validation",
							list(arrInitialResponse),
							"""tupResponse""" None,
							"""exception""" exception,
							"""mxExtraInfo""" list("Schema" : strSchema)
						)

						"""TODO """
						file_put_contents(
							BASE_PATH."/LOG/validation/".$this->_strFunctionName,
							"Schema ".$strSchema.": ".PHP_EOL.$exception->getMessage().PHP_EOL.var_export($mxResult, true),
							FILE_APPEND
						)
					else:
						raise BSI_Exception(os.linesep + "Function (out) " + self._strFunctionName + ": " + os.linesep + exception.message, \
											BSI_Exception.GENERIC_PRIVATE_ERROR)