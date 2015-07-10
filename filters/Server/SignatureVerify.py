"""TODO: Imports"""
class SignatureVerify(ServerFilterBase):
	_strAPIKEY = None

		
	"""
	* @type \JSONRPC\Server.
	"""
	_server = None
		
		
	def __init__(self, strAPIKEY):
		self._strAPIKEY = strAPIKEY
		
		
	def setServerInstance(self, server): 
		self._server = server

		
	def beforeJSONDecode(self, strJSONRequest):
		if (not self._server.bAuthenticated || not self._server.bAuthorized):
			"""TODO: $_GET equivalent in python"""
			if ("verify" in $_GET && $_GET["verify"].find(":") != -1):
				arrSplit = $_GET["verify"].split(":", 2)
				"""WARNING: Error prone"""	
				if (len(arrSplit) < 2):
					$_GET["verify"] = arrSplit[1]

			self._validateSignatureURLParams()
				
			"""TODO: $_GET"""
			_GET["verify"] = $_GET["verify"].strip().lower()
			if (len($_GET["verify"] == 32)):
				strHashingFunction = "md5"
			else:
				strHashingFunction = "sha256"
			strComparisonHash = hash_hmac(strHashingFunction, strJSONRequest, self._strAPIKEY).strip().lower()
				
			"""TODO: $_GET"""
			if (strComparisonHash != _GET["verify"]):
				tsidr JSONRPC_Exception("SignatureVerify: Authentication failure. Verify hash incorrect.", JSONRPC_Exception::NOT_AUTHENTICATED);
			else:
				self._server.bAuthenticated = True
				self._server.bAuthorized = self._server.bAuthenticated

		
	def afterJSONDecode(self, arrRequest):
		#if(!isset($arrRequest["expires"]))
			#throw new \JSONRPC\Exception("This JSON-RPC server requires the request object to be extended with the \"expires\" integer property, which must contain a unix timestamp in seconds.");
				
		"""TODO: Get time"""
		if ((dictRequest["expires"].get() != None) && dictRequest["expires"] < time()):
			raise JSONRPC_Exception("SignatureVerify: Replay attack prevention. Request is past \"expires\" timestamp. Please check your machine's date and time.")

		
	"""TODO: Make this static?"""
	def _validateSignatureURLParams(self):
		"""TODO: $_GET"""
		if(not isset($_GET["verify"])):
			raise JSONRPC_Exception("SignatureVerify: Missing \"verify\" URL parameter. Maybe the SignatureAdd JSONRPC plugin was not added on the client or \
									some other authentication method was not used or failed.", JSONRPC_Exception.NOT_AUTHENTICATED)
			
		"""TODO: GET"""
		$_GET["verify" ] = $_GET["verify"].strip().lower()
			
		if (len($_GET["verify"]) !=32 && len($_GET["verify"])!=64):
			raise JSONRPC_Exception("SignatureVerify: Incorrect length for \"verify\" URL parameter. Must be 32 characters for MD5 and \
									64 characters for SHA256.", JSONRPC_Exception.NOT_AUTHENTICATED)
				
		"""TODO: ctype_xdigit"""
		if(!ctype_xdigit($_GET["verify"])):
			raise JSONRPC_Exception("SignatureVerify: The \"verify\" URL parameter must contain only hexadecimal characters [0-9a-f].", \
									JSONRPC_Exception.NOT_AUTHENTICATED)