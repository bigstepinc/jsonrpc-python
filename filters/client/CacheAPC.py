"""TODO: imports"""
#use JSONRPC\Server;
#use JSONRPC\ClientFilterBase;

"""
* JSON-RPC 2.0 client filter plugin.
* Adds APC caching.
* APC cache complete clearing can be accomplished with ::clearEntireCache(), if needed.
"""
class CacheAPC(ClientFilterBase):
	"""
	* String function names as keys, integer seconds as values.
	* Zero seconds means infinite.
	* Must contain only functions which are to be cached.
	"""
	_arrFunctionToCacheSeconds = None
		
		
	"""
	* JSONRPC request object id.
	"""
	_nCallID = None
		
		
	"""
	* Result retrieve from cache.
	"""
	_strCachedJSONResponse = None
		
		
	"""
	* Wether _strCachedJSONResponse contains a successfully retrieved cached result.
	"""
	_bServingCache = False
		
		
	"""
	* Value read from _arrFunctionToCacheSeconds.
	"""
	_nCacheSeconds = None


   	"""
	* Helps isolation with APC or shared caches on the same SERVER_NAME or otherwise.
	"""
	_strIsolationKeyAppend = ""
		
	"""
	* Cache store key.
	"""
	_strCacheKey_temporary = None
		
		
	def __init__(self, arrFunctionToCacheSeconds, strIsolationKeyAppend = ""):
		self._arrFunctionToCacheSeconds = arrFunctionToCacheSeconds
           self._strIsolationKeyAppend = strIsolationKeyAppend
		
	"""WARNING: Removed & reference"""
	def beforeJSONEncode(self, arrRequest):
		if (dictRequest["method"] in self._arrFunctionToCacheSeconds):
			"""TODO: md5"""
			self._strCacheKey_temporary = dictRequest["method"] + "_" + md5(json.dumps(dictRequest["params"]))
			if ("lang" in dictRequest):
				self._strCacheKey_temporary += "_" + dictRequest["lang"]
			"""TODO: _SERVER"""
			if (isset($_SERVER["SERVER_NAME"])):
				self._strCacheKey_temporary += $_SERVER["SERVER_NAME"]
   			self._strCacheKey_temporary += self._strIsolationKeyAppend
			
			self._strCachedJSONResponse = apc_fetch(self._strCacheKey_temporary, self._bServingCache)
			
			if (self._bServingCache):
				self._nCallID = dictRequest["id"]
			else:
				"""TODO: Check type of arrFunctionToCacheSeconds"""
				self._nCacheSeconds = self._arrFunctionToCacheSeconds[dictRequest["method"]]
		else:
			self._bServingCache = False
			self._strCacheKey_temporary = None
		
	"""WARNING: Eliminated & reference"""
	def makeRequest(self, strJSONRequest, strEndpointURL, bCalled):
		if (self._bServingCache):
			bCalled = True
			return self._strCachedJSONResponse
		
		
	"""WARNING: Eliminated & reference"""
	"""TODO: This looks ugly. Change the aspect"""
	def afterJSONDecode(self, dictResponse):
		if (not self._bServingCache \
				&& isinstance(self._strCacheKey_temporary, basestring) \
				&& isinstance(dictResponse, dict) \
				&& "result" in dictResponse
				&& "error" not in dictResponse):

			assert(dictResponse["jsonrpc"] == Server.JSONRPC_VERSION)
			"""WARNING: Not sure if this should be set to None or deleted completely"""
			dictResponse["jsonrpc"] = None
			dictResponse["id"] = None
			
			apc_store(self._strCacheKey_temporary, json.dumps(dictResponse), self._nCacheSeconds)
			
			dictResponse["jsonrpc"] = Server.JSONRPC_VERSION
			dictResponse["id"] = self._nCallID
			
		if (self._bServingCache):
			dictResponse["jsonrpc"] = Server.JSONRPC_VERSION
			dictResponse["id"] = self._nCallID
				
			self._strCachedJSONResponse = None
		
		
	"""WARNING: Make this static?"""
	def clearEntireCache(self):
		apc_clear_cache()
		apc_clear_cache("system")
		apc_clear_cache("user")
		apc_clear_cache("opcode")
