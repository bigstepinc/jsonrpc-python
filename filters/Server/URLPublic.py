"""TODO: Imports"""
class URLPublic(ServerFilterBase):
	_arrEncryptionKeys = None
	_strAPIKEY = None
	_strKeyIndex = None
	_server = None
		
		
	def __init__(self, arrEncryptionKeys, strKeyIndex, strAPIKEY):
		self._arrEncryptionKeys = arrEncryptionKeys
		self._strKeyIndex = strKeyIndex
		self._strAPIKEY = strAPIKEY

	def setServerInstance(self, server):  
		self._server = server
				
	"""WARNING: Removed & reference"""
	def beforeJSONDecode(self, strJSONRequest):
		"""TODO: $_GET"""
		strJSONRequest = self.PublicURLParamsToJSONRequest($_GET)
					
		"""TODO: Import module precedes the function call"""	
		"""TODO: Encapsulate this in try...except because of the json_last_error"""
		dictRequest = decodeJSONSafely(strJSONRequest)
		"""
		if (json_last_error()!==JSON_ERROR_NONE):
			throw new \JSONRPC\Exception("Failed to decode URL request.");
		"""

		dictRequest["id"] = None
		"""WARNING: Import"""
		dictRequest["jsonrpc"] = Server.JSONRPC_VERSION			
		dictRequest["method"] = dictRequest["m"]
		dictRequest["params"] = dictRequest["p"]
		"""WARNING: Not sure if this should be set to None or deleted completely"""
		dictRequest["m"] = None
		dictRequest["p"] = None
			
		if (dictRequest.get("e") != None):
			dictRequest["expires"] = dictRequest["e"]
			"""WARNING: Not sure if this should be set to None or deleted completely"""
			dictRequest["e"] = None
				
			"""TODO: time"""
			if (dictRequest["expires"] < time()):
				raise JSONRPC_Exception("Replay attack prevention. Request is past \"expires\" timestamp.", JSONRPC_Exception.REQUEST_EXPIRED)
			
				
		#PublicURLParamsToJSONRequest throws if something goes wrong.
		self._server.bAuthenticated = True
		self._server.bAuthorized = self._server.bAuthenticated
			
		"""WARNING: Check if it's json.dumps or loads"""
		strJSONRequest = json.dumps(dictRequest)


		
	"""
	* Returns a HTTP URL with the function call with the request HTTP param encrypted so that the link can be exposed in browsers, e-mails, etc.
	* Functions called by a JSONRPC URL do not have to return in JSONRPC format necessarily, and may instead issue HTTP redirects, render HTML documents, force downloads, etc.
	* @param string strEndpointURL.
	* @param string strFunctionName.
	* @param array dictParams.
	* @param int nMaxAgeSeconds = None.
	"""
	def URLRequestGenerate(self, strEndpointURL, strFunctionName, dictParams, nMaxAgeSeconds = None, nMode = self.MODE_AES_128):
		dictRequest = {"m"=>$strFunctionName, "p"=>$arrParams}
		if (nMaxAgeSeconds != None):
			"""TODO: time"""
			dictRequest["e"] = time() + int(nMaxAgeSeconds)
			
		"""WARNING: Check if it's json.dumps or loads"""
		return self.JSONRequestToPublicURL(strEndpointURL, json.dumps(dictRequest), nMode)
		
		
	def URLParamDecrypt(self, strBase64Data, strIV):
		"""TODO: base64_decode"""
		strEncryptedData = base64_decode(strBase64Data, True)
		if (strEncryptedData == False):
			raise Exception("Base64 input contains characters outside of the base64 character set.")

		strIVBytes = self.hex2raw(strIV)
		
		"""TODO: mcrypt_decrypt"""
		strDecryptedCompressed = mcrypt_decrypt(MCRYPT_RIJNDAEL_128, self._dictEncryptionKeys[self._strKeyIndex], strEncryptedData, MCRYPT_MODE_CBC, strIVBytes)
			
		"""TODO: gzinflate"""
		strReturn = gzinflate(strDecryptedCompressed)
			
		return basestring(strReturn)

		
	def URLParamDecode(self, strBase64Data):
		"""TODO: base64_decode"""
		strGzDeflatedData = base64_decode(strBase64Data, True)
		if (strGzDeflatedData == False):
			raise Exception("Base64 input contains characters outside of the base64 character set.")
			
		strReturn = gzinflate(strGzDeflatedData)
			
		return basestring(strReturn)
		

	def URLParamEncrypt(self, strData, strIV):
		"""TODO: gzdeflate"""
		strCompressedData = gzdeflate(strData, 9)
		if (strCompressedData == False):
			raise Exception("Failed to compress data before encryption.")
			
		strIVBytes = self.hex2raw(strIV)
		
		"""TODO: mcrypt_decrypt"""
		strEncryptedData = mcrypt_encrypt(MCRYPT_RIJNDAEL_128, self._dictEncryptionKeys[self._strKeyIndex], strCompressedData, MCRYPT_MODE_CBC, strIVBytes)
			
		"""TODO: base64_encode"""
		strBase64 = base64_encode(strEncryptedData)
			
		#if(md5($this->URLParamDecrypt($strBase64, self::raw2hex($strIVBytes)))!=md5($strData))
			#throw new \Exception("Encrypted data failed decryption test.");
			
		return strBase64
		
		
	def JSONRequestToPublicURL(self, strRequestURL, strJSONRequest, nMode = self.MODE_AES_128):
		"""TODO: check if PublicRequest is arr or dict"""
		if (nMode == self.MODE_PLAIN):
			dictPublicRequest = self.JSONRequestToURLPlainParams(strJSONRequest)			
		elif (nMode == self.MODE_AES_128):
			dictPublicRequest = self.JSONRequestToURLEncryptedParams(strJSONRequest)
		elif (nMode == self.MODE_BASE64):
			dictPublicRequest = self.JSONRequestToURLBase64Params(strJSONRequest)
		else :
			raise JSONRPC_Exception("Unknown mode specified")
			
		if (int(nMode) != """default""" self.MODE_AES_128):
			dictPublicRequest["m"] = int(nMode)
		
		if (strRequestURL.find("?") != -1):
			strRequestURL += "&"
		else:
			strRequestURL += "?"
			
		#Does not check for existing URL params. Either way, deduplication or overwriting must be considered a conflict and must be resolved.
		"""TODO: http_build_query"""
		strRequestURL += http_build_query(arrPublicRequest)

		return strRequestURL
		
		
	def PublicURLParamsToJSONRequest(self, dictParams, bEmptyOnError = False):
		try:
			"""TODO: Check if EncryptionKeys is dict or arr"""
			for (strKeyIndex, strKey in self._dictEncryptionKeys):
				if (dictParams.get(strKeyIndex) != None):
					self._strKeyIndex = strKeyIndex
						
					"""TODO: str_replace"""
					dictParams[strKeyIndex] = str_replace(" ", "+", dictParams[strKeyIndex]) #invalid text transform text mail clients fix
					
					"""TODO: base64_decode"""
					strVerify = self.raw2hex(base64_decode(self.base64URLUnescape(dictParams["v"]), True))
						
					"""TODO: continue"""
					if ("m" in dictParams):
						nMode = int(dictParams["m"])
					else:
						nMode = self.MODE_AES_128

					if (nMode == self.MODE_AES_128):
						"""TODO: base64URLUnescape"""
						strJSONRequest = self.URLParamDecrypt(self.base64URLUnescape(dictParams[strKeyIndex]), strVerify, strKeyIndex)
					elif (nMode == self.MODE_PLAIN):
						strJSONRequest = dictParams[strKeyIndex]
					elif (nMode == self.MODE_BASE64):
						"""TODO: base64URLUnescape"""
						strJSONRequest = self.URLParamDecode(self.base64URLUnescape(dictParams[strKeyIndex]))
					else: 
						raise JSONRPC_Exception("Unknown mode specified") 

					strSignatureForComparison = self.JSONRequestSignatureAndIV(strJSONRequest)
						
					if (strSignatureForComparison != strVerify):
						raise JSONRPC_Exception("Authentication failure. Verify hash incorrect.", JSONRPC_Exception.NOT_AUTHENTICATED)
					
					return strJSONRequest
				
			raise JSONRPC_Exception("Invalid params.")
		except Exception as exc:
			if (bEmptyOnError):
				"""TODO: Check if it's json.dumps or loads"""
				return json.dumps([])
			raise exc
		
		
	def JSONRequestToURLEncryptedParams(self, strJSONRequest):
		strIVAndSignature = self.JSONRequestSignatureAndIV(strJSONRequest)
			
		strEncryptedParam = self.URLParamEncrypt(strJSONRequest, strIVAndSignature)
			
		dictProtectedOptions = {self._strKeyIndex : self.base64URLEscape(strEncryptedParam),
								"""TODO: base64URLEscape"""
								"v" : self.base64URLEscape(base64_encode(self.hex2raw(strIVAndSignature)))}
			
		return dictProtectedOptions


	def JSONRequestToURLPlainParams(self, strJSONRequest):
		strIVAndSignature = self.JSONRequestSignatureAndIV(strJSONRequest)
		
		dictProtectedOptions = {self._strKeyIndex : strJSONRequest, 
								"""TODO: base64URLEscape"""
								"""TODO: base64_encode"""
								"v" : self.base64URLEscape(base64_encode(self.hex2raw(strIVAndSignature)))}
			
		return dictProtectedOptions
		

	def JSONRequestToURLBase64Params(self, strJSONRequest):
		strIVAndSignature = self.JSONRequestSignatureAndIV(strJSONRequest)
		
		"""TODO: gzdeflate"""
		strCompressedData=gzdeflate(strJSONRequest, 9)
		if (strCompressedData == False):
			raise Exception("Failed to compress data.")
		"""TODO: base64_encode"""		
		strBase64 = base64_encode(strCompressedData)
			
		dictProtectedOptions = {self._strKeyIndex : self.base64URLEscape(strBase64),
								"v" : self.base64URLEscape(base64_encode(self.hex2raw(strIVAndSignature)))}
			
		return dictProtectedOptions
		
	def JSONRequestSignatureAndIV(self, strJSONRequest):
		"""TODO: hash_hmac"""
		return hash_hmac("md5", strJSONRequest, self._strAPIKEY).lower()
		
		
	"""TODO: Make this static?"""
	def base64URLEscape(self, strBase64):
		"""TODO: str_replace"""
		return str_replace(array("+", "/", "="), array("-", "_", "" /*.*/), strBase64)

		
	"""TODO: Make this static?"""
	def base64URLUnescape(self, strBase64URLSafe):
		"""TODO: str_replace"""
		return str_replace(array("-", "_", "."), array("+", "/", "="), strBase64URLSafe)
		
		
	"""TODO: Make this static?"""
	def hex2raw(self, strHexString):
		strRawBytes = ""
		arrChunks = strHexString.split(" ", 2)
		for (i in range(len(arrChunks))):
			strRawBytes += chr(int(arrChunks[i], 16))
		return strRawBytes
		
	"""TODO: Make this static?"""
	def raw2hex(self, s):
		op = ""
		for (i in range(len(s))):
			op += hex(ord(s[i])).zfill(2)
		return op

	MODE_AES_128 = 0
	MODE_PLAIN = 1
	MODE_BASE64 = 2
