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
		"""
		if ((len(strJSONRequest) == 0) && isset($_SERVER["REQUEST_METHOD"]) && $_SERVER["REQUEST_METHOD"]=="GET"):
			rapidClient = Client(self._strPublishEndpointURL)
						
			bSSLMode = isset($_SERVER["HTTPS"]) && $_SERVER["HTTPS"]=="on"
			strFullURL = (bSSLMode ? "https://":"http://") + $_SERVER["HTTP_HOST"]
			
			if(
				($bSSLMode && (int)$_SERVER["SERVER_PORT"]!=443)
				|| (!$bSSLMode && (int)$_SERVER["SERVER_PORT"]!=80)
			)
				$strFullURL.=":".(int)$_SERVER["SERVER_PORT"];
				$strFullURL.=$_SERVER["REQUEST_URI"];
		"""
				
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

