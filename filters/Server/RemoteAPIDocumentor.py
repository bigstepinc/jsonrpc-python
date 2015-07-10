"""TODO: Imports"""
class RemoteAPIDocumentor(ServerFilterBase):
	"""TODO: Check comments"""

	"""
	 * @var string
	"""
	_strPublishEndpointURL = None
	
		
	"""
	 * @var int
	"""
	_nProjectVersionID = None
		
		
	"""
	 * @var array
	"""
	_objOptions = None
		
		
	"""
	* @var \JSONRPC\Server
	"""
	_server = None
		
		
	"""
	 * @param string strPublishEndpointURL 
	 * @param int nProjectVersionID 
	 * @param array objOptions = None
	"""
	def __init__(self, strPublishEndpointURL, nProjectVersionID, objOptions = None):
		self._nProjectVersionID = nProjectVersionID
		self._strPublishEndpointURL = strPublishEndpointURL
		self._objOptions = objOptions

		
	"""
	 * @param \JSONRPC\Server $server 
	 * 
	 * @return None
	"""
	def setServerInstance(self, server):  
		self._server = server
		
	"""WARNING: Removed & reference"""
	def beforeJSONDecode(self, strJSONRequest):
		"""TODO: Server thing"""
		if ((len(strJSONRequest) == 0) and os.environ.get("REQUEST_METHOD") != None and os.environ.get("REQUEST_METHOD") == "GET"):
			rapidClient = Client(self._strPublishEndpointURL)
						
			bSSLMode = os.environ.get("HTTPS") != None and os.environ.get("HTTPS") == "on"
			if bSSLMode:
				strFullURL = "https://" + os.environ.get("HTTP_HOST")
			else:
				strFullURL = "http://" + os.environ.get("HTTP_HOST")
			
			if(
				(bSSLMode and int(os.environ.get("SERVER_PORT")) != 443) \
				or (not bSSLMode and int(os.environ.get("SERVER_PORT")) !=80 )
			):
				strFullURL += ":" + str(int(os.environ.get("SERVER_PORT")))
				strFullURL += os.environ.get("REQUEST_URI")
				
			strHTMLDocumentation = rapidClient.published_html_interface(
				self._nProjectVersionID,
				strFullURL,
				self._strPublishEndpointURL,
				self._server.arrAllowedFunctionCalls,
				self._objOptions
			)
				
			
			"""TODO: header"""	
			header("Content-type: text/html; charset=utf-8")
			
			print strHTMLDocumentation
				
			exit(0)

