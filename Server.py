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
		
		
		public function processRequest($strJSONRequest=NULL)
		{
			$this->_exitWithResponse($this->processRequestAndReturn($strJSONRequest));
		}
		
		
		public function processRequestAndReturn($strJSONRequest)
		{
			$objReflectionPlugin=new ReflectionPlugin();
			$objReflectionPlugin->setServerInstance($this);

			if(isset($_SERVER["REQUEST_METHOD"]) && !in_array($_SERVER["REQUEST_METHOD"], array("GET", "POST", "PUT", "OPTIONS")))
			{
				echo "HTTP request method ".$_SERVER["REQUEST_METHOD"]." ignored.";
				exit(0);
			}


			$mxRequestID=NULL;
			try
			{
				//php://input must be read here only for normal HTTP POST JSON-RPC requests.
				if(is_null($strJSONRequest) && (!isset($_SERVER["REQUEST_METHOD"]) || $_SERVER["REQUEST_METHOD"]=="POST"))
					$strJSONRequest=file_get_contents("php://input");

				
				foreach($this->arrFilterPlugins as $plugin) 
				{
					$plugin->beforeJSONDecode($strJSONRequest);
				}

				
				if(!strlen(trim($strJSONRequest)))
					throw new \JSONRPC\Exception("Invalid request. Empty input. Was expecting a POST request of a JSON.", \JSONRPC\Exception::PARSE_ERROR);
				
				
				$arrRequest=static::decodeJSONSafely($strJSONRequest);
				
				
				if(isset($arrRequest[0]))
					throw new \JSONRPC\Exception("JSON-RPC batch requests are not supported by this server.", \JSONRPC\Exception::INVALID_REQUEST);
					

				if(isset($arrRequest["method"]) && is_string($arrRequest["method"]) && strlen(trim($arrRequest["method"])) && array_key_exists("params", $arrRequest))
				{
					$this->arrFunctionReflection = null;

					try 
					{	
						$this->arrFunctionReflection = $objReflectionPlugin->reflectionFunction($arrRequest["method"]);
					} 
					catch (\Exception $e) 
					{
                        //Ignoring because the reflection is expected to sometimes fail here.
                        //The reflection will be retried later where it is not expected to fail.
                        //One of these tries must succeed to obtain the functions reflection object.
					}

					if(!is_null($this->arrFunctionReflection))
					{
						$this->namedParamsTranslationAndValidation($this->arrFunctionReflection["function_params"], $arrRequest["params"], $arrRequest["method"]);
						$this->validateDataTypes($this->arrFunctionReflection["function_params"], $arrRequest["params"]);
					}
				}

				
				foreach($this->arrFilterPlugins as $plugin) 
					$plugin->afterJSONDecode($arrRequest);
			

				//A String containing the name of the method to be invoked. 
				//Method names that begin with the word rpc followed by a period character (U+002E or ASCII 46)
				//are reserved for rpc-internal methods and extensions and MUST NOT be used for anything else.
				if(
					!isset($arrRequest["method"]) 
					|| !is_string($arrRequest["method"]) 
					|| !strlen(trim($arrRequest["method"]))
				)
					throw new \JSONRPC\Exception("The \"method\" key must be a string with a function name.", \JSONRPC\Exception::INVALID_REQUEST);
				
				
				
				//A Structured value that holds the parameter values to be used during the invocation of the method.
				//This member MAY be omitted.
				if(!array_key_exists("params", $arrRequest))
					$arrRequest["params"]=array();
				
				if(!is_array($arrRequest["params"]))
					throw new \JSONRPC\Exception("The \"params\" key must be an array.", \JSONRPC\Exception::INVALID_REQUEST);


				
				if(is_callable($arrRequest["method"]) || function_exists($arrRequest["method"]))
				{
					$this->arrFunctionReflection=$objReflectionPlugin->reflectionFunction($arrRequest["method"]);
					$this->namedParamsTranslationAndValidation($this->arrFunctionReflection["function_params"], $arrRequest["params"], $arrRequest["method"]);
					$this->validateDataTypes($this->arrFunctionReflection["function_params"], $arrRequest["params"]);
				}



				if(
                    isset($_SERVER["REQUEST_METHOD"])
					&& $_SERVER["REQUEST_METHOD"]==="OPTIONS" 
					&& !in_array($arrRequest["method"], $this->arrAllowedFunctionCallsFor_HTTP_OPTIONS)
				)
				{
					echo "HTTP request method ".$_SERVER["REQUEST_METHOD"]." ignored.";
					exit(0);
				}



				//An identifier established by the Client that MUST contain a String, Number, or NULL value if included. 
				//If it is not included it is assumed to be a notification. 
				//The value SHOULD normally not be Null and Numbers SHOULD NOT contain fractional parts.
				$this->bNotificationMode=!array_key_exists("id", $arrRequest);
				
				if(!$this->bNotificationMode && !is_int($arrRequest["id"]) && !is_null($arrRequest["id"]))
					throw new \JSONRPC\Exception("The \"id\" key must be an integer, a null or be omitted for Notification requests.", \JSONRPC\Exception::INVALID_REQUEST);
				
				if(!$this->bNotificationMode)
					$mxRequestID=$arrRequest["id"];
				
				
				
				//A String specifying the version of the JSON-RPC protocol. MUST be exactly "2.0".
				if(!isset($arrRequest["jsonrpc"]) || $arrRequest["jsonrpc"]!=self::JSONRPC_VERSION)
					throw new \JSONRPC\Exception("The \"jsonrpc\" version must be equal to ".self::JSONRPC_VERSION, \JSONRPC\Exception::INVALID_REQUEST);
				
				
				
				$this->assertFunctionNameAllowed($arrRequest["method"]);
				
				
				
				//Safe-guard, so developers don't accidentally open the RPC server to the world (default is false, not authenticated).
				//Exceptions should be thrown by authentication filters.
				//Authentication filters must set JSONRPC_server::$bAuthenticated to true upon successfull authentication.
				if(!$this->bAuthenticated)
					throw new \JSONRPC\Exception("Not authenticated (bad credentials or signature).", \JSONRPC\Exception::NOT_AUTHENTICATED);
				
				
				//Safe-guard, so developers don't accidentally open the RPC server to any user account (default is false, not authorized).
				//Exceptions should be thrown by authorization filters.
				//Authorization filters must set JSONRPC_server::$bAuthorized to true upon successfull authorization.
				if(!$this->bAuthorized)
					throw new \JSONRPC\Exception("Authenticated user is not authorized.", \JSONRPC\Exception::NOT_AUTHORIZED);
					
				
				$arrResponse=array("result"=>null);
				$arrResponse["result"]=$this->callFunction($arrRequest["method"], $arrRequest["params"]);
				
				if(isset($this->arrFunctionReflection) && count($this->arrFunctionReflection))
					$this->returnDataTypeValidation($arrRequest["method"], $this->arrFunctionReflection["function_return_type"], $arrResponse["result"]);

				if(!$this->nHTTPResponseCode)
				{
					if($this->bNotificationMode)
						$this->nHTTPResponseCode=self::HTTP_204_NO_CONTENT;
					else
						$this->nHTTPResponseCode=self::HTTP_200_OK;
				}
			}
			catch(\Exception $exc)
			{
				try
				{
					$this->_log_exception($exc);
					
					//Gives a chance to log the original Exception and/or throw another "translated" Exception.
					//If nothing is thrown inside exceptionCatch, this catch block will rethrow the original Exception anyway.
					foreach($this->arrFilterPlugins as $plugin)
						$plugin->exceptionCatch($exc);
					throw $exc;
				}
				catch(\Exception $exc)
				{
					$arrResponse=$this->_exceptionToJSONResponse($exc);
				}
			}
			
			$arrResponse["jsonrpc"]=self::JSONRPC_VERSION;
			if(!$this->bNotificationMode)
				$arrResponse["id"]=$mxRequestID;
			
            
    		try
            {
                foreach($this->arrFilterPlugins as $plugin)
        			$plugin->response($arrResponse);
            }
            catch(\Exception $exc)
            {
                $this->_log_exception($exc);
                
                if(!isset($arrResponse["error"]))
                    $arrResponse=$this->_exceptionToJSONResponse($exc);
            }
            
			
			return $arrResponse;
		}
		
        
        /**
        * Will affect the HTTP status.
        */
        protected function _exceptionToJSONResponse(\Exception $exc)
        {
            $strExceptionClass=get_class($exc);
			while(substr($strExceptionClass, 0, 1)=="\\")
			{
				$strExceptionClass=substr($strExceptionClass, 1);
			}
			
    		
			if(in_array($strExceptionClass, $this->arrExceptionTypesForMessages))
			{
				$strMessage=$exc->getMessage();
			}
			else if($this->bDebugAllowAllExceptionMessages)
			{
				$strMessage=
					"[Internal error: ".$strExceptionClass."] ".$exc->getMessage()." "
					.PHP_EOL.$exc->getFile()."#".$exc->getLine()." "
					.PHP_EOL.$exc->getTraceAsString()
				;
			}
			else
			{
				$strMessage="Internal error.";
			}
				
			
			if(in_array($strExceptionClass, $this->arrExceptionTypesForCodes))
				$nCode=(int)$exc->getCode();
			else
				$nCode=0;
			
			
			if(!$this->nHTTPResponseCode)
			{
				if(
					in_array($nCode, array(
						\JSONRPC\Exception::NOT_AUTHENTICATED, 
						\JSONRPC\Exception::NOT_AUTHORIZED
					))
				)
				{
					$this->nHTTPResponseCode=self::HTTP_403_FORBIDDEN;
				}
				else
				{
					$this->nHTTPResponseCode=self::HTTP_500_INTERNAL_SERVER_ERROR;
				}
			}
			
			$arrResponse["error"]=array(
				"message"=>$strMessage,
				"code"=>$nCode,
			);
            
            return $arrResponse;
        }
        
		
		protected function _exitWithResponse(array $arrResponse)
		{
			$this->_http_response_code($this->nHTTPResponseCode);
			$this->_header("Cache-Control: no-cache, must-revalidate");
			$this->_header("Expires: Mon, 26 Jul 1991 05:00:00 GMT");
			$this->_header("Accept-Ranges: none");
			$this->_header("Connection: close");
			$this->_header("Content-type: application/json");
			//self::_header("Content-type: text/plain;charset=utf-8");
			
			
			/**
			* JSON-RPC 2.0 Specification, 4.1 Notification
			* Notifications are not confirmable by definition, since they do not have a Response object to be returned. 
			* As such, the Client would not be aware of any errors (like e.g. "Invalid params","Internal error").
			*/
			if(!$this->bNotificationMode)
				echo json_encode($arrResponse);
			
			if(in_array($this->nHTTPResponseCode, array(
				self::HTTP_200_OK, 
				self::HTTP_204_NO_CONTENT,
			)))
			{
				exit(0);
			}
			exit(1);
		}

		
		public function callFunction($strFunctionName, array $arrParams)
		{
			ignore_user_abort(true);
			
			$this->assertFunctionNameAllowed($strFunctionName);
			
			foreach($this->arrFilterPlugins as $plugin)
				$plugin->resolveFunctionName($strFunctionName);
			
			
			$bCalled=false;
			foreach($this->arrFilterPlugins as $pluginExisting)
			{
				$mxResult=$pluginExisting->callFunction($strFunctionName, $arrParams, $bCalled);
				if($bCalled)
					break;
			}
			
			if(!$bCalled)
			{
				if(!is_callable($strFunctionName))
				{
					$callable=$this->functionNameToCallableArray($strFunctionName);
					$mxResult=call_user_func_array($callable, $this->array_make_references($arrParams));
				}
				else
				{
					$mxResult=call_user_func_array($strFunctionName, $this->array_make_references($arrParams));
				}
			}
				
			return $mxResult;
		}
		
		
		public function addFilterPlugin(\JSONRPC\ServerFilterBase $plugin)
		{
			foreach($this->arrFilterPlugins as $pluginExisting)
				if(get_class($pluginExisting)==get_class($plugin))
					return;
			$plugin->setServerInstance($this);
			$this->arrFilterPlugins[]=$plugin;
		}
		
		
		public function removeFilterPlugin(\JSONRPC\ServerFilterBase $plugin)
		{
			$nIndex=NULL;
			foreach($this->arrFilterPlugins as $nIndexExisting=>$pluginExisting)
				if(get_class($pluginExisting)==get_class($plugin))
				{
					$nIndex=$nIndexExisting;
					break;
				}
			if(!is_int($nIndex))
				throw new \Exception("Failed to remove filter plugin object, maybe plugin is not registered.");
			
			array_splice($this->arrFilterPlugins, $nIndex, 1);
		}
		
		
		public function addMethodsMapper(\JSONRPC\MethodsMapper $methodsMapper)
		{
			foreach($this->arrMethodsMappers as /*$strInstanceAPIClassNameExisting =>*/ $methodsMapperExisting)
			{
				if($methodsMapperExisting===$methodsMapper)
				{
					return;
				}
			}
			$this->arrMethodsMappers[get_class($methodsMapper->instanceWithAPIMethods())]=$methodsMapper;
		}
		
		
		public function removeMethodsMapper(\JSONRPC\MethodsMapper $methodsMapper)
		{
			
			$strInstanceAPIClassNameExisting=get_class($methodsMapper->instanceWithAPIMethods());
			
			if(array_key_exists($strInstanceAPIClassNameExisting, $this->arrMethodsMappers))
			{
				unset($this->arrMethodsMappers[$strInstanceAPIClassNameExisting]);
			}
			else
			{
				throw new \Exception("Failed to remove methodsMapper object.");
			}
		}
		
		
		public function methodsMappers()
		{
			return $this->arrMethodsMappers;
		}
		
		
		/**
		 * @param string $strFunctionName
		 * 
		 * @return callable
		 */
		public function functionNameToCallableArray($strFunctionName)
		{
			foreach($this->methodsMappers() as /*$strInstanceAPIClassName =>*/ $methodsMapper)
			{
				if(array_key_exists($strFunctionName, $methodsMapper->arrAPIFunctionsNamesToMethodsNames()))
				{
					// Returning callable "type".
					return array(
						/*Class instance*/ 0=>$methodsMapper->instanceWithAPIMethods(),
						/*Method name*/ 1=>$methodsMapper->arrAPIFunctionsNamesToMethodsNames()[$strFunctionName],
					);
				}
			}
			
			throw new \JSONRPC\Exception("The function ".$strFunctionName." is not defined or loaded.", \JSONRPC\Exception::METHOD_NOT_FOUND);
		}
		
		
		/**
		 * @param string $strFunctionName 
		 * 
		 * @throws \JSONRPC\Exception 
		 * @return null
		 */
		public function assertFunctionNameAllowed($strFunctionName)
		{
			$bFunctionNameAllowed=false;
			foreach($this->arrFilterPlugins as $plugin)
			{
				$bFunctionNameAllowed=$plugin->isFunctionNameAllowed($strFunctionName);
				
				if($bFunctionNameAllowed)
				{
					break;
				}
			}

			if(!$bFunctionNameAllowed && !in_array($strFunctionName, $this->arrAllowedFunctionCalls))
			{
				$this->nHTTPResponseCode=self::HTTP_403_FORBIDDEN;
				throw new \JSONRPC\Exception("The function \"".$strFunctionName."\" is not exported and/or does not exist.", \JSONRPC\Exception::METHOD_NOT_FOUND);
			}
		}
		
		
		/**
		* Safely decode JSON strings, because json_decode() does not throw errors.
		* @param string $strJSON.
		* @param bool $bAssoc.
		* @return mixed.
		* @throws \JSONRPC\Exception.
		*/
		public static function decodeJSONSafely($strJSON, $bAssoc=true)
		{
			if(strlen(trim($strJSON))==0)
			{
				throw new \PHorse\Utils\JSONException("Cannot run json_decode() on empty string.", \JSONRPC\Exception::PARSE_ERROR);
			}
			
			$mxReturn=json_decode($strJSON, $bAssoc);
			
			if(json_last_error()!=JSON_ERROR_NONE)
			{
				throw new \JSONRPC\Exception(
					"JSON deserialization failed. Error message: ".json_last_error_msg().PHP_EOL." RAW input: ".$strJSON, 
					\JSONRPC\Exception::PARSE_ERROR
				);
			}

			return $mxReturn;
		}
		
		
		public function &array_make_references(array &$arrSomething)
		{ 
			$arrAllValuesReferencesToOriginalValues=array();
			foreach($arrSomething as $mxKey=>&$mxValue)
				$arrAllValuesReferencesToOriginalValues[$mxKey]=&$mxValue;
			return $arrAllValuesReferencesToOriginalValues;
		}
		
		
		protected function _log_exception(\Exception $exception)
		{
			try
			{
				if(strlen($this->strErrorLogFilePath))
				{
					$strClientInfo="";
					if(array_key_exists("REMOTE_ADDR", $_SERVER))
						$strClientInfo.=" ".$_SERVER["REMOTE_ADDR"];
					if(array_key_exists("HTTP_USER_AGENT", $_SERVER))
						$strClientInfo.=" ".$_SERVER["HTTP_USER_AGENT"];
					
					try
					{
						$arrTrace=$exception->getTrace();

						if(preg_match_all('@*RECURSION*@', print_r($arrTrace, true), $arrMatches))
							throw new \Exception("Recursive stack trace.");

						$strTrace=var_export($arrTrace, true);
						$strTrace.=PHP_EOL."Short trace: ".PHP_EOL.$exception->getTraceAsString();
					}
					catch(\Exception $exc)
					{
						$strTrace=$exception->getTraceAsString();
					}

					$strError=
						$exception->getFile()."#".$exception->getLine().PHP_EOL.
						"Exception type: ".get_class($exception).PHP_EOL.
						"Message: ".$exception->getMessage().PHP_EOL.
						"Code: ".$exception->getCode().PHP_EOL.
						$strTrace.PHP_EOL
					;

					if(!file_exists(dirname($this->strErrorLogFilePath)))
					{
						mkdir(dirname($this->strErrorLogFilePath), 0777, true);
					}
					error_log($strError, 3, $this->strErrorLogFilePath);
				}
			}
			catch(\Exception $exc)
			{
				echo "Failed error logging at ".__FILE__."#".__LINE__;
				echo ", exception code ".json_encode($exc->getCode()).", exception message: ".$exc->getMessage().", stack trace: ".PHP_EOL;
				echo $exc->getTraceAsString();
				echo PHP_EOL;
				echo "Failed to log this line: ".PHP_EOL.$strErrorLine;
				
				exit(1);
			}
		}
		
		
		const HTTP_200_OK=200;
		const HTTP_204_NO_CONTENT=204;
		const HTTP_401_UNAUTHORIZED=401;
		const HTTP_403_FORBIDDEN=403;
		const HTTP_429_TOO_MANY_REQUESTS=429;
		const HTTP_500_INTERNAL_SERVER_ERROR=500;
		
		protected function _http_response_code($nHTTPResponseCode)
		{
			if(!$this->nHTTPResponseCode)
				$this->nHTTPResponseCode=self::HTTP_500_INTERNAL_SERVER_ERROR;
			
			static $arrHTTPResponseCodesToText=array(
				self::HTTP_200_OK=>"OK",
				self::HTTP_204_NO_CONTENT=>"No Content",
				self::HTTP_401_UNAUTHORIZED=>"Unauthorized",
				self::HTTP_403_FORBIDDEN=>"Forbidden",
				self::HTTP_429_TOO_MANY_REQUESTS=>"Too Many Requests",
				self::HTTP_500_INTERNAL_SERVER_ERROR=>"Internal Server Error",
			);
			$this->_header("HTTP/1.1 ".(int)$nHTTPResponseCode." ".$arrHTTPResponseCodesToText[(int)$nHTTPResponseCode], /*$bReplace*/ true, $nHTTPResponseCode);
		}
		
		
		protected function _header($strHeader, $bReplace=true)
		{
			static $_bHTTPMode=null;
			
			if(is_null($_bHTTPMode))
			{
				$_bHTTPMode=(
					array_key_exists("REQUEST_METHOD", $_SERVER)
					&& in_array(
						$_SERVER["REQUEST_METHOD"], 
						array("GET", "POST", "PUT", "HEAD", "DELETE", "OPTIONS", "TRACE", "CONNECT")
					)
				);
			}
			
			
			if($_bHTTPMode)
			{
				header($strHeader, $bReplace);
			}
		}
		
		const JSONRPC_VERSION="2.0";


		public function isAssociativeArray(array $array)
		{
			if(!is_array($array))
				return false;

			//http://stackoverflow.com/a/4254008/1852030
			return (bool)count(array_filter(array_keys($array), "is_string"));
		}

		public function validateDataTypes(array $arrParamsDetails, array &$arrParams)
		{
			if(!$this->bValidateTypes)
				return;
				
			for ($i=0; $i < count($arrParamsDetails); $i++)
			{
				$strParamName = $arrParamsDetails[$i]["param_name"];

				if(!array_key_exists($i, $arrParams))
				{
					if(strlen($arrParamsDetails[$i]["param_default_value_json"]) == 0)
						throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "] is mandatory and doesn't have a default value.", \JSONRPC\Exception::INVALID_PARAMS);
					else
						return;
				}

				if(is_null($arrParams[$i]) && $arrParamsDetails[$i]["param_default_value_json"] !== "null")
					throw new \JSONRPC\Exception("Parameter " . $strParamName . " cannot be NULL.", \JSONRPC\Exception::INVALID_PARAMS);
				
				if (is_null($arrParams[$i]))
					continue;

				switch ($arrParamsDetails[$i]["param_type"])
				{
					case "integer":

						if(is_int($arrParams[$i]))
							break;

						if(
							!is_string($arrParams[$i])
							|| (string)(int)$arrParams[$i] !== (string)$arrParams[$i]
						)
						{
							throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "], must be an integer (Number JSON type with no decimals), " . gettype($arrParams[$i]) . " given.", \JSONRPC\Exception::INVALID_PARAMS);
						}

						$arrParams[$i] = (int) $arrParams[$i];

						break;		


					case "float":

						if(is_float($arrParams[$i]) || is_int($arrParams[$i]))
							break; 
						
						if(!is_string($arrParams[$i]) || (string)(float)$arrParams[$i] !== $arrParams[$i])
							throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "], must be a Number., " . gettype($arrParams[$i]) . " given.", \JSONRPC\Exception::INVALID_PARAMS);

						$arrParams[$i] = (float) $arrParams[$i];

						break;					

					
					case "boolean":

						if(is_bool($arrParams[$i]))
							break;

						if(is_array($arrParams[$i]) || is_object($arrParams[$i]))
						{
							throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "], must be Boolean, " . gettype($arrParams[$i]) . " given.", \JSONRPC\Exception::INVALID_PARAMS);
						}
							
						if((string)$arrParams[$i] === "0")
							$arrParams[$i] = false;
						else if((string)$arrParams[$i] === "1")
							$arrParams[$i] = true;
						else
							throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "], must be Boolean, " . gettype($arrParams[$i]) . " given.", \JSONRPC\Exception::INVALID_PARAMS);

						break;


					case "array":

						if(!is_array($arrParams[$i]))
						{
							throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "], must be an Array, " . gettype($arrParams[$i]) . " given.", \JSONRPC\Exception::INVALID_PARAMS);
						}
						else if($this->isAssociativeArray($arrParams[$i]))
						{
							throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "], must be an Array, Object (key:value collection) given.", \JSONRPC\Exception::INVALID_PARAMS);
						}

						break;


					case "object":
						if(!is_array($arrParams[$i]))
						{
							throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "], must be an Object, " . gettype($arrParams[$i]) . " given.", \JSONRPC\Exception::INVALID_PARAMS);
						}
						else if(
							!$this->isAssociativeArray($arrParams[$i]) 
							&& !is_object($arrParams[$i]) 
							&& !(
								is_array($arrParams[$i]) 
								&& !count($arrParams[$i])
							)
						)
						{
							throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "], must be an Object (key:value collection), " . gettype($arrParams[$i]) . " given.", \JSONRPC\Exception::INVALID_PARAMS);
						}

						break;


					case "string":

						if(is_string($arrParams[$i]))
							break;

						if (!is_string($arrParams[$i]) && !is_int($arrParams[$i]))
							throw new \JSONRPC\Exception("Parameter at index " . $i . " [" . json_encode($strParamName) . "], must be a String, ".json_encode($arrParams[$i])." given.", \JSONRPC\Exception::INVALID_PARAMS);

						$arrParams[$i] = (string) $arrParams[$i];

						break;

					case "mixed":
						break;


					default:
						throw new \JSONRPC\Exception("Unhandled type ".json_encode($arrParamsDetails[$i]["param_type"]).".", \JSONRPC\Exception::INVALID_PARAMS);
				}
			}
		}


		public function returnDataTypeValidation($strMethodName, $strExpectedDataType, &$mxResult)
		{
			if(!$this->bValidateTypes)
				return;
			
			if($strExpectedDataType=="mixed")
				return;
			
			if($strExpectedDataType=="unknown")
				return;
			
			if(
				is_array($mxResult) 
				&& $strExpectedDataType=="object" 
				&& (
					$this->isAssociativeArray($mxResult) 
					|| count($mxResult)==0
				)
			)
			{
				$mxResult=(object)$mxResult;
			}
			else if(is_int($mxResult) && $strExpectedDataType=="float")
				$mxResult=(float)$mxResult;
			
			
			$strReturnType=gettype($mxResult);
			
			if($strReturnType=="double")
				$strReturnType="float";
			
			
			if(strtolower($strReturnType) != strtolower($strExpectedDataType))
				throw new \JSONRPC\Exception("Method ".json_encode($strMethodName)." declared return type is ".$strExpectedDataType.", and it attempted returning ".$strReturnType.". The function call may have succeeded as it attempted to return.", \JSONRPC\Exception::INVALID_RETURN_TYPE);
		}


		public function namedParamsTranslationAndValidation(array $arrParamsDetails, array &$arrParams, $strMethodName)
		{
			//Count number of mandatory parameters
			$nMandatoryParams = 0;

			foreach ($arrParamsDetails as $arrParam) 
			{
				if(strlen($arrParam["param_default_value_json"]) == 0)
					$nMandatoryParams++;
				else
					break;
			}


			if(count($arrParams) > 0 && $this->isAssociativeArray($arrParams))
			{
				//Named parameteres
				$arrNewParams = array();

				foreach ($arrParamsDetails as $arrParamProperties) 
				{
					if(array_key_exists($arrParamProperties["param_name"], $arrParams))
						$arrNewParams[] = $arrParams[$arrParamProperties["param_name"]];
					else if(strlen($arrParamProperties["param_default_value_json"]) > 0)
						$arrNewParams[] = $arrParamProperties["param_default_value_json"];
					else
						throw new \JSONRPC\Exception("Missing mandatory method parameter " . json_encode($arrParamProperties["param_name"]) . " for method " . json_encode($strMethodName) . ".", \JSONRPC\Exception::INVALID_PARAMS);
				
					unset($arrParams[$arrParamProperties["param_name"]]);
				}


				if(count($arrParams) > 0)
					throw new \JSONRPC\Exception("Too many parameters given to method " . json_encode($strMethodName) . ". Extra parameters: " . json_encode(array_keys($arrParams)) . ".", \JSONRPC\Exception::INVALID_PARAMS);
					
				$arrParams = $arrNewParams;
			}
			else 
			{
				//Unnamed params

				if(count($arrParams) > count($arrParamsDetails))
					throw new \JSONRPC\Exception("Expected param(s): ".$this->getParamNamesAsString($arrParamsDetails)."."." Too many parameters for method ".$strMethodName.".", \JSONRPC\Exception::INVALID_PARAMS);
					
				if(count($arrParams) < $nMandatoryParams)
					throw new \JSONRPC\Exception("Expected param(s): ".$this->getParamNamesAsString($arrParamsDetails)."."." Missing ".($nMandatoryParams-count($arrParams))." required parameter(s) for method ".$strMethodName.".", \JSONRPC\Exception::INVALID_PARAMS);
			}
		}

		public function getParamNamesAsString(array $arrParamsDetails)
		{
			$strParamNames = "";

			foreach ($this->getParamNames($arrParamsDetails) as $param)
				$strParamNames.= $param.", ";
			
			$strParamNames = substr($strParamNames, 0, (strlen($strParamNames)-2));
			return $strParamNames;
		}


		public function getParamNames(array $arrParamsDetails)
		{
			$arrParamsName = array();

			if(count($arrParamsDetails) > 0)
				foreach ($arrParamsDetails as $value) 
					if(strlen($value["param_default_value_json"]) > 0)
						$arrParamsName[] = $value["param_name"] . "=" . $value["param_default_value_json"];					
					else
						$arrParamsName[] = $value["param_name"];	

			return $arrParamsName;
		}
		
		
		/**
		* Outputs HTTP cross site origin headers.
		* This function never returns if during an HTTP OPTIONS request, as it will exit(0) at the end.
		* @param array $arrAllowedDomains.
		* @param array $arrAllowedHeaders=array(). Headers in addition to those allowed by default ["origin", "content-type", "accept"].
		* @param bool $bAllowAllURLs=false.
		* @return null.
		*/
		public function CORS_headers(array $arrAllowedDomains, array $arrAllowedHeaders=array(), $bAllowAllURLs=false)
		{
			// Note .htaccess trick: 
			// SetEnvIf Origin "^http(s)?://(.+\.)?(localhost|stackoverflow.com|example1.com)(:[0-9]+)?$" origin_is=$0
			// Header always set Access-Control-Allow-Origin %{origin_is}e env=origin_is
			
			
			$strAllowedOrigin=NULL;

			
			$arrAllowedHeaders=array_merge($arrAllowedHeaders, array("origin", "content-type", "accept", "authorization"));
			
			if(isset($_SERVER["HTTP_ORIGIN"]))
			{
				$strHost=parse_url($_SERVER["HTTP_ORIGIN"], PHP_URL_HOST);
				
				if(in_array($strHost, $arrAllowedDomains))
					$strAllowedOrigin=$_SERVER["HTTP_ORIGIN"];
			}

			//if(is_null($strAllowedOrigin) && count($arrAllowedDomains))
				//$strAllowedOrigin="https://".implode(", https://", $arrAllowedDomains).", http://".implode(", http://", $arrAllowedDomains);
				
			if($bAllowAllURLs)
				header("Access-Control-Allow-Origin: *", true);
			else if(!is_null($strAllowedOrigin))
				header("Access-Control-Allow-Origin: ".$strAllowedOrigin, true);
			else if(isset($_SERVER["REQUEST_METHOD"]) && $_SERVER["REQUEST_METHOD"]=="OPTIONS")
				exit(0);
				
			header("Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT", true);
			header("Access-Control-Max-Age: 86400", true);
			header("Access-Control-Allow-Headers: ".implode(", ", $arrAllowedHeaders), true);
			header("Access-Control-Allow-Credentials: true", true);
			
			if(isset($_SERVER["REQUEST_METHOD"]) && $_SERVER["REQUEST_METHOD"]=="OPTIONS")
				exit(0);
		}
		
	
		
	}
}