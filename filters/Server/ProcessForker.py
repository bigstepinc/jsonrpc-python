"""TODO: Imports"""

"""
 * JSONRPC_server plugin that overrides the client's 
"""
class ProcessForker(ServerFilterBase):
	"""
	 *	@var int nIOTimeout The IO operations timeout in microseconds.
	"""
	_nIOTimeout = self.IO_TIMEOUT_INFINITE
		
		
	"""
	 * @var array arrStreamStates Array of objects with the saved states of the following
	 * streams: STDIN, STDOUT and STDERR.
	"""
	_arrStreamStates = []
	
		
	"""TODO: Modify this"""
	"""
	 * @var \JSONRPC\Server
	"""
	_objServer = None
		
		
	"""
	 * Class constructor used to alter the used timeouts.
	 *
	 * @param int nIOTimeout The IO operations timeout. Defaults to ProcessForker.IO_TIMEOUT_INFINITE.
	 *
	 * @return None
	"""
	def __init__(self, nIOTimeout = self.IO_TIMEOUT_INFINITE):
			self._nIOTimeout = nIOTimeout

	"""TODO: Add data about parameters"""
	"""
	 * @override
	"""
	def setServerInstance(self, server): 
		self._objServer = server

		
	"""
	 * Reads the request from STDIN and updates the strJSONRequest to the read value.
	 *
	 * @param string strJSONRequest The JSON request reference that will be replaced with
	 * the read JSON request.
	 * 
	 * @return None
	"""
	"""WARNING: Removed & reference"""
	def beforeJSONDecode(self, strJSONRequest):
		"""TODO: wtf is this?"""
		if (strcasecmp(php_sapi_name(), "cli")):
			raise Exception("Invalid SAPI. The process forker requires CLI SAPI.")
		
			arrStreams = [STDIN, STDOUT, STDERR]
		
		for (hStreamHandle in arrStreams):
			"""TODO: Check this out"""
			if (!stream_is_local(hStreamHandle)):
				raise Exception("The STDIN, STDOUT and STDERR streams must be local.")
				
		self._saveStreamStates()
		
		"""TODO: Set blocking"""	
		stream_set_blocking(STDIN, /*$blocking*/ (int)false)
			
		"""
		 * No synchronization needed. The data is already in the STDIN file. 
		"""
		strJSONRequest = ProcessForkerClient.fread(STDIN, self._nIOTimeout)
		if (strJSONRequest == False):
			raise Exception("STDIN read failed. The request couldn't be read.")
				
		self._restoreStreamStates()
			
		# Same server request.
		self._objServer.bAuthenticated = True
		self._objServer.bAuthorized = True
		
		
	"""
	 * Saves the current stream states of the following streams for future restoration: STDIN, 
	 * STDOUT and STDERR.
	 *
	 * @return None
	"""
	"""TODO: Check indentation. It could have some errors."""
	def _saveStreamStates(self):
			arrStreams = [ProcessForkerClient.STDIN : STDIN, ProcessForkerClient.STDOUT : STDOUT, ProcessForkerClient.STDERR : STDERR]
		
			"""TODO: CHeck arrStreams for naming consistency"""
			for (nStreamIndex, hStreamHandle in arrStreams):
				"""TODO: stream_get_meta_data"""
				self._arrStreamStates[nStreamIndex] = stream_get_meta_data(hStreamHandle)
		
	"""
	 * Restores the following streams to their previously saved states: STDIN, STDOUT and
	 * STDERR.
	 *
	 * @return None
	"""
	def _restoreStreamStates(self):
		for (nStreamIndex, objStreamState in self._arrStreamStates):
			hStreamHandle = None
		
			"""Observation: Switch emulation"""
			if (nStreamIndex == ProcessForkerClient.STDIN):
				hStreamHandle = STDIN
				#break
						
			elif (nStreamIndex == ProcessForkerClient.STDOUT):
				hStreamHandle = STDOUT
				#break
						
			elif (nStreamIndex == ProcessForkerClient.STDERR):
				hStreamHandle = STDERR
				#break
					
			else:
				raise Exception("Invalid saved stream index. You've reached unreachable code.")
							
			""" The plugin modified only the blocking property. """
			"""TODO: stream_set_blocking"""
			stream_set_blocking(hStreamHandle, objStreamState["blocked"])
		
	
	IO_TIMEOUT_INFINITE = -1

