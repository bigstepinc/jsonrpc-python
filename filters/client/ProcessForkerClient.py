"""
* Client plugin that overrides the client's default synchronous behaviour making it
* asynchronous. 
* 
* It creates new CLI processes on the same machine with the client and
* sends them requests via pipes/files. It can be used to launch multiple functions in parallel
* on child processes and to control these processes.
"""
"""TODO: imports"""
import tempfile
import os.path
import os.linesep

class ProcessForkerClient(ClientFilterBase):
	"""
	 * @staticvar object _JSONRPCClient Client instance used to access the
	 * processRAWResponse method.
	"""
	_JSONRPCClient = None


	"""
	 * @var array _arrEnvironmentVariables The environment variables to pass to the child
	 * processes.
	"""
	_arrEnvironmentVariables = []

	"""
	 * @var array _objNewProcess An object containing information about the
	 * new process to be started.
	 *	{
	 * 		"callback" : JSONRPC_proces_forker_callback,
	 *		"config" : JSONRPC_proces_forker_config,
	 * 		"handle" : $hProcessHandle,
	 * 		"pipes" : {
	 * 			1 : hStdout,
	 * 			2 : hStderr
	 * 		},
	 *		"start_timestamp" : microtime(true)?,
	 *		"call_id" : $nCallID,
	 *		"buffers" : {
	 * 			1 : "",
	 * 			2 : ""
	 *		},
	 *		"output" : ""
	 * 	}.
	"""
	_objNewProcess = None

		
	"""
	 * @var array _arrRunningProcesses An array of objects containing information about all
	 * the failed processes indexed by the call ID in the same format of the running processes
	 * array.
	"""
	_arrRunningProcesses = []

		
	"""
	 * @var string _strTemporaryDirectoryPath The temporary directory to use for temporary
	 * files.
	"""
	_strTemporaryDirectoryPath = None

		
	"""
	 * @var string _strLogFilePath The path of the log file to use. Should be set to None
	 * to disable logging.
	"""
	_strLogFilePath = None


	"""
	 * Class constructor that initializes the child environment.
	 *
	 * @param array arrEnvironmentVariables The environment variables that need to be
	 * passed to the child processes.
	 * 
	 * @return None
	"""
	def __init__(self, arrEnvironmentVariables = [], strTemporaryDirectoryPath = None, strLogFilePath = None):
		"""TODO: Get ENV"""
		"""
		self._arrEnvironmentVariables = array_merge(
			$_ENV,
			/* ENV is no longer populated with the environment variables. */
			array(
				"PATH" => getenv("PATH")
			),
			$arrEnvironmentVariables
		);
		"""

		if (strTemporaryDirectoryPath == None):
			strTemporaryDirectoryPath = tempfile.gettempdir() #Use system temporary directory.
		elif (isinstance(strTemporaryDirectoryPath, basestring)):
			raise Exception("Invalid temporary directory path. It must be a string.")
		elif (os.path.exists(strTemporaryDirectoryPath)):
			"""Observation: Directory creation is not recursive"""
			os.mkdir(strTemporaryDirectoryPath, 0777, true)

		self._strTemporaryDirectoryPath = strTemporaryDirectoryPath
		self._strLogFilePath = strLogFilePath

		
	"""
	 * Extracts the callback function and memorizes it.
	 *
	 * @param array arrRequest The request body.
	"""
	"""WARNING: Removed & reference"""
	def beforeJSONEncode(self, arrRequest):
		assert ((isinstance(arrRequest["id"], int) == True) and (arrRequest["id"] > 0))
		assert (self._objNewProcess == None)
		assert (not arrRequest["id"] in self._arrRunningProcesses)

		"""WARNING: Check class instance"""
		if (arrRequest["params"][0] != None and isinstance(arrRequest["params"][0], object) \
			and isinstance(arrRequest["params"][0], JSONRPC_Filters_Client_ProcessForkerConfig)):
			"""WARNING: This should work, but not entirely sure"""
			self._objNewProcess["config"] = arrRequest["params"].pop()
		else:
			self._objNewProcess["config"] = ProcessForkerConfig()

		if((arrRequest["params"][0] != None) and isinstance(arrRequest["params"][0], object) \
			and isinstance(arrRequest["params"][0], JSONRPC_Filters_Client_ProcessForkerCallback)):
			self._objNewProcess["callback"] = arrRequest["params"].pop()
		else:
			self._objNewProcess["callback"] = None

		self._objNewProcess["call_id"] = arrRequest["id"]
		
		
	"""
	 * Creates a new process and sends the request.
	 *
	 * Returns an "asynchronous" fake JSONRPC successful response.
	 * 
	 * strEndpointFilePath is the endpoint file path (stand alone executable or excecutable with script) which will receive JSONRPC CLI arguments.
	 * The executable path and each argument (if any) must have already been properly escaped using escapeshellarg().
	 * 
	 * 
	 * @param string strJSONRequest The JSON encoded request.
	 * @param string strEndpointFilePath The endpoint file path (stand alone executable or excecutable with script) which will receive JSONRPC CLI arguments.
	 * @param bool bCalled Set to true to signal JSONRPC_Server not to invoke makeRequest on other plugins.
	 *
	 * @return string
	"""
	"""WARNING: Removed & reference"""
	def makeRequest(self, strJSONRequest, strEndpointFilePath, bCalled):
		bCalled = True

		objNewProcess = self._objNewProcess
		self._objNewProcess = None
			
		"""TODO: Create temporary file"""
		#strStdinTmpFile = tempfile.TemporaryFile(self._strTemporaryDirectoryPath, self.TEMPORARY_FILE_NAME_PREFIX + "STDIN_");
			
		if(strStdinTmpFile == False):
			raise Exception("STDIN file creation failed.")
			
		try:
			"""Observation: Use with when opening files in python"""
			hStdinTmpFile = open(strStdinTmpFile, "w")

			"""WARNING: I think this exception is thrown automatically"""
			"""
			if (!is_resource($hStdinTmpFile))
			{
				throw new \Exception("STDIN file open failed.");
			}
			"""

			# Set the file to unblocking in order to avoid the process to hang when writing. 
			"""TODO: Set blocking """
			"""
			if (!stream_set_blocking($hStdinTmpFile, /*$blocking*/ (int)false))
			{
				throw new \Exception("Making the STDIN stream non-blocking failed.");
			}
			"""

			"""CONTINUE"""
			""" Write to the STDIN file before creating a child process to avoid synchronization. """
			if (not self.fwrite(hStdinTmpFile, strJSONRequest)):
				raise Exception("STDIN file write failed. The JSON request couldn't be written.")

			"""Don't need the file any more. Ignore fclose failure. """
			hStdinTmpFile.close()

			dictDescriptor = {self.STDIN : ["file", strStdinTmpFile, "r"],
							self.STDOUT : ["pipe", "w"],
							self.STDERR : ["pipe", "w"]}

			if (objNewProcess["config"].runAsPrivilegedUser()):
				strPrepend = "sudo -n -E "
			else:
				strPrepend = ""

			""" 
			* Change the behaviour of the proc_open function by using exec. Avoid the creation
			* of an additional shell process. 
			"""
			"""TODO"""
			"""
			objNewProcess["handle"] = proc_open(
				"exec ".$strPrepend." ".$strEndpointFilePath,
				$arrDescriptor,
				$objNewProcess["pipes"],
				NULL, /* default cwd path */
				$this->_arrEnvironmentVariables
			);
			"""
			"""WARNING: Remove this. Just add try/except"""
			if (not isinstance(objNewProcess["handle"], file)):
				raise Exception("Child process creation failed.")

			objNewProcess["buffers"] = []
			for nProcessPipeIndex in objNewProcess["pipes"].keys():
				"""WARNING: Error prone"""
				objNewProcess["buffers"][nProcessPipeIndex] = ""

			"""TODO: Measure time"""
			objNewProcess["start_timestamp"] = microtime(true)
			self._arrRunningProcesses[objNewProcess["call_id"]] = objNewProcess

			try:
				for nProcessPipeIndex, hProcessPipe in objNewProcess["pipes"]:
					"""WARNING: Encapsulate these in try/except"""
					"""TODO: Set blocking"""
					if (isinstance(hProcessPipe, file) or (not stream_set_blocking(hProcessPipe, int(False)))):
						self._killProcess(objNewProcess["call_id"])
						raise Exception("Process pipe is invalid.")
			except Exception as exc:
				self._closeProcess(objNewProcess["call_id"])
				raise exc
		finally:
			"""
			* The file will be deleted when it won't be used by a process any more. The file is
			* opened by the current process. Unlink doesn't throw exceptions.
			"""
			"""TODO: Check if file exists"""
			"""TODO: Check unlink"""
			if (file_exists(strStdinTmpFile)):
				unlink(strStdinTmpFile)


		self._log("Call #" + objNewProcess["call_id"] + " initiated with request: " + strJSONRequest + ".")

		""" Synchronous behaviour if no callback has been specified. """
		if (objNewProcess.get("callback") == None):
			arrFinishedProcesses = self._waitRequests(self.SELECT_TIMEOUT_DEFAULT_USEC, [objNewProcess["call_id"]])
			assert(len(arrFinishedProcesses) == 1)

			objFinishedProcess = arrFinishedProcesses.pop()
			assert(objFinishedProcess["call_id"] == objNewProcess["call_id"])

			assert("output" in objFinishedProcess)
			if (isinstance(objFinishedProcess["output"], object)):
				assert(isinstance(objFinishedProcess["output"], Exception))
				raise objFinishedProcess["output"]

			"""WARNING: Error prone"""
			return objFinishedProcess["buffers"][self.STDOUT]

		dictFakeSuccess = {"result" : None, "id" : objNewProcess["call_id"], "jsonrpc" : Server.JSONRPC_VERSION}

		"""WARNING: Check if it's dumps or loads"""
		return json.dumps(arrFakeSuccess)
		

	"""
	 * Wait for some child processes to finish execution and execute the callbacks if any.
	 * The infinite IO timeout may delay the processing of other calls and cause the processes
	 * to be allowed to run more then their set timeout. Ignore timeouts when the processes
	 * start to output data.
	 *
	 * Returns the number of finished processes.
	 * 
	 * @param int nSelectTimeout The select timeout in microseconds. Defaults to -1
	 * (INFINITE).
	 *
	 * @return int
	"""
	def selectRequests(self, nSelectTimeout = -1):
		return len(self._selectRequests(nSelectTimeout))

		
	"""
	 * Wait for all the processes to finish execution and execute the callbacks if any.
	 * The infinite IO timeout may delay the processing of other calls and cause the processes
	 * to be allowed to run more then their set timeout. Ignore timeouts when the processes
	 * start to output data.
	 *
	 * @param int nSelectTimeout The select timeout in microseconds. Defaults to -1
	 * (INFINITE).
	 *
	 * @return None
	"""
	def waitRequests(self, nSelectTimeout = -1):
		self._waitRequests(nSelectTimeout)

		

	"""
	 * Wait for some child processes to finish execution and execute the callbacks if any.
	 * The infinite IO timeout may delay the processing of other calls and cause the processes
	 * to be allowed to run more then their set timeout. Ignore timeouts when the processes
	 * start to output data.
	 *
	 * Returns the finished processes.
	 * 
	 * @param int nSelectTimeout The select timeout in microseconds. Defaults to -1
	 * (INFINITE).
	 * @param array arrCallIDs The calls to wait for.
	 *
	 * @return array
	"""
	def _selectRequests(self, nSelectTimeout, arrCallIDs = None):
		""" Lazy initialization. """
		if (self._JSONRPCClient == None):
			self._JSONRPCClient = Client(None)

		nSelectTimeoutSec = 0

		""" The select function uses None as a value for INFINITE. """
		if (nSelectTimeout == -1):
			nSelectTimeout = None
			nSelectTimeoutSec = None

		""" Create the select array. """
		arrStdoutAndStderrProcessPipes = []

		for objProcess in _arrRunningProcesses:
			if ((arrCallIDs == None) or objProcess["call_id"] in arrCallIDs):
				arrStdoutAndStderrProcessPipes.append(objProcess["pipes"][self.STDOUT])
				arrStdoutAndStderrProcessPipes.append(objProcess["pipes"][self.STDERR])

		""" If there are no running processes return. """
		if (len(arrStdoutAndStderrProcessPipes) == 0):
			return 0

		""" Avoid select error. """
		Null = None

		""" 
		 * Select doesn't work on windows for pipes opened by proc_open function. If a process
		 * dies before it could output anything the select function will consider the STDOUT and
		 * STDERR pipes ready for reading. 
		"""
		nNoOfEvents = stream_select(arrStdoutAndStderrProcessPipes, Null, Null, nSelectTimeoutSec, nSelectTimeout)
		if (nNoOfEvents == False):
			raise Exception("Process pipes select failed.")

		arrFinishedProcesses = []
		"""TODO: Measure time"""
		fCurrentTimestamp = microtime(true);

		"""WARNING: Removed & reference"""
		for objRunningProcess in self._arrRunningProcesses:
			try:
				for nProcessPipeIndex, hProcessPipe in objRunningProcess["pipes"]:
					"""
					 * Removed condition. Lead to timeouts. The pipe is set to non-blocking so the read should
					 * be instantaneous even of there is no data to be read. The stream_select call is used more
					 * like a sleep. 
					"""
					objRunningProcess["buffers"][nProcessPipeIndex] += self.fread(hProcessPipe)
					
				nProcessEndStatus = self._waitProcess(objRunningProcess["call_id"], 0)
				if (nProcessEndStatus == False):
					"""WARNING: Error prone"""
					if (objRunningProcess["buffers"].get(self.STDOUT) == None	and \
						objRunningProcess["buffers"].get(self.STDERR) == None):
						
						fProcessTimeout = objRunningProcess["config"].getTimeout()
						"""TODO: Measure time"""
						if (fProcessTimeout != -1 and (fCurrentTimestamp - objRunningProcess["start_timestamp"]) > fProcessTimeout):
							raise Exception("Process timed out.")
				
				"""WARNING: Error prone"""
				"""TODO: Find out what feof does"""
				if (objRunningProcess["buffers"].get(self.STDERR) == None and feof(objRunningProcess["pipes"][self::STDERR])):
					raise Exception("Process encountered an error with the following message: " + objRunningProcess["buffers"][self::STDERR] + ".")
						
				"""TODO: Find out what feof does"""
				if (nProcessEndStatus == False or not feof(objRunningProcess["pipes"][self.STDOUT]) \
					or not feof(objRunningProcess["pipes"][self.STDERR])):
					continue
				
				"""WARNING: May have to change mxProcessOutput. There is no mixed type in python"""	
				mxProcessOutput = self._JSONRPCClient.processRAWResponse(objRunningProcess["buffers"][self.STDOUT], False)

			except Exception as e:
				self._killProcess(objRunningProcess["call_id"])
				mxProcessOutput = e

			"""TODO: Check var_export"""
			self._log("Call #" + objRunningProcess["call_id"] + " finished with output: " + var_export(mxProcessOutput, true) + ".")

			"""TODO: Check if class exists"""
			assert(class_exists("JSONRPC\\Filters\\Client\\ProcessForkerCallback"))


			"""TODO: Solve this"""
			if (isinstance(objRunningProcess["callback"], object) and not strcasecmp(get_class(objRunningProcess["callback"]), "JSONRPC\\Filters\\Client\\ProcessForkerCallback")):
				objRunningProcess["callback"].call(mxProcessOutput)
				objRunningProcess["output"] = mxProcessOutput

			arrFinishedProcesses.append(objRunningProcess)

			self._closeProcess(objRunningProcess["call_id"])
			
		"""TODO: Unset"""
		unset(objRunningProcess)

		return arrFinishedProcesses

		
	"""TODO: Check documentation"""
	"""
	 * Wait for all the processes to finish execution and execute the callbacks if any.
	 * The infinite IO timeout may delay the processing of other calls and cause the processes
	 * to be allowed to run more then their set timeout. Ignore timeouts when the processes
	 * start to output data.
	 *
	 * Returns the finished processes.
	 * 
	 * @param int nSelectTimeout The select timeout in microseconds. Defaults to -1
	 * (INFINITE).
	 * @param array arrCallIDs The calls to wait for.
	 *
	 * @return array
	"""
	def _waitRequests(self, nSelectTimeout = -1, arrCallIDs = None):
		nRunningProcesses = len(self._arrRunningProcesses)

		if (arrCallIDs == None):
			"""WARNING: Check if arrCallIDs is list/dict/tuple"""
			assert(isinstance(arrCallIDs, list))

			for objRunningProcess in self._arrRunningProcesses:
				if (objRunningProcess["call_id"] not in arrCallIDs):
					nRunningProcesses -= 1

			assert(len(arrCallIDs) == nRunningProcesses)

		arrFinishedProcesses = []

		while (nRunningProcesses > 0):
			arrCurrentlyFinishedProcesses = self._selectRequests(nSelectTimeout, arrCallIDs)
			nRunningProcesses -= len(arrCurrentlyFinishedProcesses)

			arrFinishedProcesses = arrFinishedProcesses + arrCurrentlyFinishedProcesses
	
		return arrFinishedProcesses

	"""TODO: Check documentation. Replace mixed"""
	"""
	 * Waits for a process to finish execution with a timeout.
	 *
	 * @TODO: Rewrite it to use select.
	 *
	 * Returns the exit code or false if the process times out.
	 * 
	 * @param int nCallID The ID of the call.
	 * @param int nTimeout The timeout to use. It defaults to -1(INFINITE).
	 *
	 * @return not mixed
	"""
	def _waitProcess(self, nCallID, nTimeout = -1):
		assert(nCallID in self._arrRunningProcesses)

		"""TODO: Measure time"""
		nStartTime = microtime(true)

		"""Emulation of a do...while"""
		while (True):
			"""WARNING: Error prone"""
			arrProcessStatus = proc_get_status(self._arrRunningProcesses[nCallID]["handle"])
			if(not arrProcessStatus["running"]):
				return arrProcessStatus["exitcode"]
			"""TODO: Measure time"""
			if ((nTimeout == -1) or ((microtime(true) - nStartTime) <= nTimeout)):
				break
		return False

	"""
	 * Closes a process. If the process is still running it blocks until it exits.
	 *
	 * Returns the process end status.
	 * 
	 * @param int nCallID The ID of the call.
	 *
	 * @return int
	"""
	def _closeProcess(self, nCallID):
		assert(nCallID in self._arrRunningProcesses)

		""" Close the pipes to avoid deadlock. """
		for hProcessPipe in self._arrRunningProcesses[nCallID]["pipes"]:
			hProcessPipe.close()
			""" Ignore its output."""

		nExitCode = proc_close(self._arrRunningProcesses[nCallID]["handle"])

		"""TODO: Unset. Not sure if set to None or delete"""
		self._arrRunningProcesses[nCallID] == None

		return nExitCode

		
	"""
	 * Signals a process.
	 *
	 * Returns the process status.
	 * 
	 * @param int nCallID The ID of the call.
	 * @param int nSignalCode The UNIX signal code.
	 *
	 * @return int
	"""
	def _signalProcess(self, nCallID, nSignalCode):
		assert(nCallID in self._arrRunningProcesses)

		return int(proc_terminate(self._arrRunningProcesses[nCallID]["handle"], nSignalCode))

		
	"""
	 * Kills a process by sending the SIGKILL UNIX signal.
	 *
	 * @param int nCallID The ID of the call.
	 *
	 * @return int. The process end status.
	"""
	def _killProcess(self, nCallID):
		return self._signalProcess(nCallID, self.SIGKILL)

		
	"""
	 * Logs a message to the the log file, in case the log file path is not null.
	 *
	 * @param string The message to log.
	 *
	 * @return None
	"""
	def _log(self, strMessage):
		if (self._strLogFilePath == None):
			return
		
		error_log(strMessage + os.linesep, 3, self._strLogFilePath)

		
	"""TODO: Read documentation"""
	"""
	 * Wrapper for the fwrite function that assures that the whole provided string has been
	 * written with a specified timeout. The file/pipe must have the unblocking property set.
	 *
	 * @TODO: Rewrite it to use select.
	 *
	 * @param resource hFileHandle The handle of the file to write to.
	 * @param string strToBeWritten The string that needs to be written to the file.
	 * @param int nTimeout The timeout to use. It defaults to -1(INFINITE).
	 *
	 * @return bool True for success or false for failure.
	"""
	"""TODO: Make this static? """
	def fwrite(self, hFileHandle, strToBeWritten, nTimeout = -1):
		assert(isinstance(hFileHandle, file))
		assert(isinstance(strToBeWritten, basestring))

		nBytesLeft = len(strToBeWritten)
		"""TODO: Measure time"""
		nStartTime = microtime(True)

		"""Observation: Emulation of do...while"""
		while (True):
			"""TODO: This is a built-in function and the above is a wrapper. Search for python equivalent of fwrite"""
			nBytesWritten = fwrite(hFileHandle, strToBeWritten, nBytesLeft)
			"""TODO: Adapt according to fwrite equivalent"""
			if (nBytesWritten != False):
				nBytesLeft -= nBytesWritten
				if (nBytesLeft <= 0):
					""" nByteLeft can't be lower than 0. """
					return True
					strToBeWritten = strToBeWritten[nBytesWritten:]

			"""TODO: Measure time"""
			if (nTimeout == -1 or (microtime(true) - nStartTime) <= nTimeout):
				break

		return False
		

	"""TODO: Check documentation"""
	"""
	 * Wrapper for the fread function that reads from a file untill it times out or it reads an empty
	 * string. The file/pipe must have the unblocking property set.
	 *
	 * @TODO: Rewrite it to use select.
	 *
	 * @param handle hFileHandle The handle of the file to read from.
	 * @param int nTimeout The timeout to use. It defaults to -1(INFINITE).
	 *
	 * @return string The read string.
	"""
	"""TODO: Make this static?"""
	def fread(self, hFileHandle, nTimeout = -1):
		assert(isinstance(hFileHandle, file))

		strReadString = ""
		"""TODO: Measure time"""
		nStartTime = microtime(true)

		"""Observation: Emulation of do...while"""
		while (True):
			strPartialReadString = fread(hFileHandle, 4096)
			if (strPartialReadString != False):
				strReadString += strPartialReadString
				if (len(strPartialReadString) == 0):
					break
			"""TODO: Measure time"""
			if (nTimeout == -1 or (microtime(true) - nStartTime) <= nTimeout):
				break

		return strReadString
		
		
	"""
	 * STDIN pipe index.
	"""
	STDIN = 0

	"""
	 * STDOUT pipe index.
	"""
	STDOUT = 1

	"""
	 * STDERR pipe index.
	"""
	STDERR = 2

	"""
	* The temporary files name prefix.
	"""
	TEMPORARY_FILE_NAME_PREFIX = "PROCESS_FORKER_"

	"""
	 * Default select timeout.
	"""
	SELECT_TIMEOUT_DEFAULT_USEC = 1000000

	"""
	 * Process termination signal.
	"""
	SIGKILL = 9

