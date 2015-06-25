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
		else if (isinstance(strTemporaryDirectoryPath, basestring)):
			raise Exception("Invalid temporary directory path. It must be a string.")
		"""Observation: Directory creation is not recursive"""
		else if (os.path.exists(strTemporaryDirectoryPath)):
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
		assert ((isinstance(arrRequest["id"], int) == True) && (arrRequest["id"] > 0))
		assert (self._objNewProcess == None)
		assert (not arrRequest["id"] in self._arrRunningProcesses)

		if (arrRequest["params"][0] != None && isinstance(arrRequest["params"][0], object) \
			"""WARNING: Check class instance"""
			&& isinstance(arrRequest["params"][0], JSONRPC_Filters_Client_ProcessForkerConfig \
		)
			"""WARNING: This should work, but not entirely sure"""
			self._objNewProcess["config"] = arrRequest["params"].pop()
		else:
			self._objNewProcess["config"] = ProcessForkerConfig()

		if((arrRequest["params"][0] != None) && isinstance(arrRequest["params"][0], object) \
			&& isinstance(arrRequest["params"][0], JSONRPC_Filters_Client_ProcessForkerCallback \
		):
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
			hStdinTmpFile = fopen(strStdinTmpFile, "w");
			if(!is_resource($hStdinTmpFile))
			{
				throw new \Exception("STDIN file open failed.");
			}

			/* Set the file to unblocking in order to avoid the process to hang when writing. */
			if(!stream_set_blocking($hStdinTmpFile, /*$blocking*/ (int)false))
			{
				throw new \Exception("Making the STDIN stream non-blocking failed.");
			}

			/* Write to the STDIN file before creating a child process to avoid synchronization. */
			if(!self::fwrite($hStdinTmpFile, $strJSONRequest))
			{
				throw new \Exception("STDIN file write failed. The JSON request couldn't be written.");
			}

			/* Don't need the file any more. Ignore fclose failure. */
			fclose($hStdinTmpFile);

			$arrDescriptor = array(
				self::STDIN => array("file", $strStdinTmpFile, "r"),
				self::STDOUT => array("pipe", "w"),
				self::STDERR => array("pipe", "w"),
			);

			if($objNewProcess["config"]->runAsPrivilegedUser())
			{
				$strPrepend = "sudo -n -E ";
			}
			else
			{
				$strPrepend = "";
			}

			/* Change the behaviour of the proc_open function by using exec. Avoid the creation
			of an additional shell process. */
			$objNewProcess["handle"] = proc_open(
				"exec ".$strPrepend." ".$strEndpointFilePath,
				$arrDescriptor,
				$objNewProcess["pipes"],
				NULL, /* default cwd path */
				$this->_arrEnvironmentVariables
			);
			if(!is_resource($objNewProcess["handle"]))
			{
				throw new \Exception("Child process creation failed.");
			}

			$objNewProcess["buffers"] = array();
			foreach(array_keys($objNewProcess["pipes"]) as $nProcessPipeIndex)
			{
				$objNewProcess["buffers"][$nProcessPipeIndex] = "";
			}

			$objNewProcess["start_timestamp"] = microtime(true);
			$this->_arrRunningProcesses[$objNewProcess["call_id"]] = $objNewProcess;

			try
			{
				foreach($objNewProcess["pipes"] as $nProcessPipeIndex => $hProcessPipe)
				{
					if(!is_resource($hProcessPipe) || !stream_set_blocking($hProcessPipe, /*$blocking*/ (int)false))
					{
						$this->_killProcess($objNewProcess["call_id"]);
						throw new \Exception("Process pipe is invalid.");
					}
				}
			}
			catch(\Exception $exc)
			{
				$this->_closeProcess($objNewProcess["call_id"]);

				throw $exc;
			}
		}
		finally
		{
			/* The file will be deleted when it won't be used by a process any more. The file is
			opened by the current process. Unlink doesn't throw exceptions.*/
			if(file_exists($strStdinTmpFile))
			{
				unlink($strStdinTmpFile);
			}
		}


		$this->_log("Call #".$objNewProcess["call_id"]." initiated with request: ".$strJSONRequest.".");

		/* Synchronous behaviour if no callback has been specified. */
		if(is_null($objNewProcess["callback"]))
		{
			$arrFinishedProcesses = $this->_waitRequests(self::SELECT_TIMEOUT_DEFAULT_USEC, array($objNewProcess["call_id"]));
			assert(count($arrFinishedProcesses) == 1);

			$objFinishedProcess = array_shift($arrFinishedProcesses);
			assert($objFinishedProcess["call_id"] == $objNewProcess["call_id"]);

			assert(array_key_exists("output", $objFinishedProcess));
			if(is_object($objFinishedProcess["output"]))
			{
				assert($objFinishedProcess["output"] instanceof \Exception);
				throw $objFinishedProcess["output"];
			}

			return $objFinishedProcess["buffers"][self::STDOUT];
		}

		$arrFakeSuccess = array(
			"result" => NULL,
			"id" => $objNewProcess["call_id"],
			"jsonrpc" => Server::JSONRPC_VERSION
		);

		return json_encode($arrFakeSuccess);
	}
		

	/**
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
	 */
	public function selectRequests($nSelectTimeout = -1)
	{
		return count($this->_selectRequests($nSelectTimeout));
	}

		
	/**
	 * Wait for all the processes to finish execution and execute the callbacks if any.
	 * The infinite IO timeout may delay the processing of other calls and cause the processes
	 * to be allowed to run more then their set timeout. Ignore timeouts when the processes
	 * start to output data.
	 *
	 * @param int nSelectTimeout The select timeout in microseconds. Defaults to -1
	 * (INFINITE).
	 *
	 * @return null
	 */
	public function waitRequests($nSelectTimeout = -1)
	{
		$this->_waitRequests($nSelectTimeout);
	}
		

	/**
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
	 */
	protected function _selectRequests($nSelectTimeout, $arrCallIDs = NULL)
	{
		/* Lazy initialization. */
		if(is_null(self::$_JSONRPCClient))
		{
			self::$_JSONRPCClient = new Client(NULL);
		}

		$nSelectTimeoutSec = 0;

		/* The select function uses NULL as a value for INFINITE. */
		if($nSelectTimeout === -1)
		{
			$nSelectTimeout = NULL;
			$nSelectTimeoutSec = NULL;
		}

		/* Create the select array. */
		$arrStdoutAndStderrProcessPipes = array();

		foreach($this->_arrRunningProcesses as $objProcess)
		{
			if(is_null($arrCallIDs) || in_array($objProcess["call_id"], $arrCallIDs))
			{
				$arrStdoutAndStderrProcessPipes []= $objProcess["pipes"][self::STDOUT];
				$arrStdoutAndStderrProcessPipes []= $objProcess["pipes"][self::STDERR];
			}
		}

		/* If there are no running processes return. */
		if(!count($arrStdoutAndStderrProcessPipes))
			return 0;

		/* Avoid select error. */
		$Null = NULL;

		/* Select doesn't work on windows for pipes opened by proc_open function. If a process
		dies before it could output anything the select function will consider the STDOUT and
		STDERR pipes ready for reading. */
		$nNoOfEvents = stream_select($arrStdoutAndStderrProcessPipes, $Null, $Null, $nSelectTimeoutSec, $nSelectTimeout);
		if($nNoOfEvents === false)
			throw new \Exception("Process pipes select failed.");

		$arrFinishedProcesses = array();
		$fCurrentTimestamp = microtime(true);

		foreach($this->_arrRunningProcesses as &$objRunningProcess)
		{
			try
			{
				foreach($objRunningProcess["pipes"] as $nProcessPipeIndex => $hProcessPipe)
				{
					/* Removed condition. Lead to timeouts. The pipe is set to non-blocking so the read should
					be instantaneous even of there is no data to be read. The stream_select call is used more
					like a sleep. */
					$objRunningProcess["buffers"][$nProcessPipeIndex] .= self::fread($hProcessPipe);
				}
					
				$nProcessEndStatus = $this->_waitProcess($objRunningProcess["call_id"], 0);
				if($nProcessEndStatus === false)
				{
					if(
						empty($objRunningProcess["buffers"][self::STDOUT])
						&& empty($objRunningProcess["buffers"][self::STDERR])
					)
					{
						$fProcessTimeout = $objRunningProcess["config"]->getTimeout();
						if($fProcessTimeout != -1 && ($fCurrentTimestamp - $objRunningProcess["start_timestamp"]) > $fProcessTimeout)
							throw new \Exception("Process timed out.");
					}
				}

				if(!empty($objRunningProcess["buffers"][self::STDERR]) && feof($objRunningProcess["pipes"][self::STDERR]))
					throw new \Exception("Process encountered an error with the following message: ".$objRunningProcess["buffers"][self::STDERR].".");
						
				if(
					$nProcessEndStatus === false
					|| !feof($objRunningProcess["pipes"][self::STDOUT])
					|| !feof($objRunningProcess["pipes"][self::STDERR])
				)
					continue;
					
				$mxProcessOutput = self::$_JSONRPCClient->processRAWResponse($objRunningProcess["buffers"][self::STDOUT], false);
			}
			catch(\Exception $e)
			{
				$this->_killProcess($objRunningProcess["call_id"]);
				$mxProcessOutput = $e;
			}

			$this->_log("Call #".$objRunningProcess["call_id"]." finished with output: ".var_export($mxProcessOutput, true).".");

			assert(class_exists("JSONRPC\\Filters\\Client\\ProcessForkerCallback"));
			if(is_object($objRunningProcess["callback"]) && !strcasecmp(get_class($objRunningProcess["callback"]), "JSONRPC\\Filters\\Client\\ProcessForkerCallback"))
				$objRunningProcess["callback"]->call($mxProcessOutput);
			$objRunningProcess["output"] = $mxProcessOutput;

			$arrFinishedProcesses []= $objRunningProcess;

			$this->_closeProcess($objRunningProcess["call_id"]);
		}
			
		unset($objRunningProcess);

		return $arrFinishedProcesses;
	}

		
	/**
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
	 */
	protected function _waitRequests($nSelectTimeout = -1, $arrCallIDs = NULL)
	{
		$nRunningProcesses = count($this->_arrRunningProcesses);

		if(!is_null($arrCallIDs))
		{
			assert(is_array($arrCallIDs));

			foreach($this->_arrRunningProcesses as $objRunningProcess)
				if(!in_array($objRunningProcess["call_id"], $arrCallIDs))
					$nRunningProcesses--;

			assert(count($arrCallIDs) == $nRunningProcesses);
		}

		$arrFinishedProcesses = array();

		while($nRunningProcesses > 0)
		{
			$arrCurrentlyFinishedProcesses = $this->_selectRequests($nSelectTimeout, $arrCallIDs);
			$nRunningProcesses -= count($arrCurrentlyFinishedProcesses);

			$arrFinishedProcesses = array_merge(
				$arrFinishedProcesses,
				$arrCurrentlyFinishedProcesses
			);
		}

		return $arrFinishedProcesses;
	}

	/**
	 * Waits for a process to finish execution with a timeout.
	 *
	 * @TODO: Rewrite it to use select.
	 *
	 * Returns the exit code or false if the process times out.
	 * 
	 * @param int nCallID The ID of the call.
	 * @param int nTimeout The timeout to use. It defaults to -1(INFINITE).
	 *
	 * @return mixed
	 */
	protected function _waitProcess($nCallID, $nTimeout = -1)
	{
		assert(array_key_exists($nCallID, $this->_arrRunningProcesses));

		$nStartTime = microtime(true);

		do
		{
			$arrProcessStatus = proc_get_status($this->_arrRunningProcesses[$nCallID]["handle"]);
			if(!$arrProcessStatus["running"])
			{
				return $arrProcessStatus["exitcode"];
			}
		}
		while($nTimeout === -1 || (microtime(true) - $nStartTime) <= $nTimeout);

		return false;
	}

	/**
	 * Closes a process. If the process is still running it blocks until it exits.
	 *
	 * Returns the process end status.
	 * 
	 * @param int nCallID The ID of the call.
	 *
	 * @return int
	 */
	protected function _closeProcess($nCallID)
	{
		assert(array_key_exists($nCallID, $this->_arrRunningProcesses));

		/* Close the pipes to avoid deadlock. */
		foreach($this->_arrRunningProcesses[$nCallID]["pipes"] as $hProcessPipe)
		{
			fclose($hProcessPipe); /* Ignore it's output. */
		}

		$nExitCode = proc_close($this->_arrRunningProcesses[$nCallID]["handle"]);

		unset($this->_arrRunningProcesses[$nCallID]);

		return $nExitCode;
	}

		
	/**
	 * Signals a process.
	 *
	 * Returns the process status.
	 * 
	 * @param int nCallID The ID of the call.
	 * @param int nSignalCode The UNIX signal code.
	 *
	 * @return int
	 */
	protected function _signalProcess($nCallID, $nSignalCode)
	{
		assert(array_key_exists($nCallID, $this->_arrRunningProcesses));

		return (int)proc_terminate($this->_arrRunningProcesses[$nCallID]["handle"], $nSignalCode);
	}

		
	/**
	 * Kills a process by sending the SIGKILL UNIX signal.
	 *
	 * @param int nCallID The ID of the call.
	 *
	 * @return int. The process end status.
	 */
	protected function _killProcess($nCallID)
	{
		return $this->_signalProcess($nCallID, self::SIGKILL);
	}

		
	/**
	 * Logs a message to the the log file, in case the log file path is not null.
	 *
	 * @param string The message to log.
	 *
	 * @return null
	 */
	protected function _log($strMessage)
	{
		if(is_null($this->_strLogFilePath))
			return;
		
		error_log($strMessage.PHP_EOL, 3, $this->_strLogFilePath);
	}

		
	/**
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
	 */
	public static function fwrite($hFileHandle, $strToBeWritten, $nTimeout = -1)
	{
		assert(is_resource($hFileHandle));
		assert(is_string($strToBeWritten));

		$nBytesLeft = strlen($strToBeWritten);
		$nStartTime = microtime(true);

		do
		{
			$nBytesWritten = fwrite($hFileHandle, $strToBeWritten, $nBytesLeft);
			if($nBytesWritten !== false)
			{
					$nBytesLeft -= $nBytesWritten;
				if($nBytesLeft <= 0) /* nByteLeft can't be lower than 0. */
					return true;
					$strToBeWritten = substr($strToBeWritten, $nBytesWritten);
			}
		}
		while($nTimeout === -1 || (microtime(true) - $nStartTime) <= $nTimeout);

		return false;
	}
		

	/**
	 * Wrapper for the fread function that reads from a file untill it times out or it reads an empty
	 * string. The file/pipe must have the unblocking property set.
	 *
	 * @TODO: Rewrite it to use select.
	 *
	 * @param handle hFileHandle The handle of the file to read from.
	 * @param int nTimeout The timeout to use. It defaults to -1(INFINITE).
	 *
	 * @return string The read string.
	 */
	public static function fread($hFileHandle, $nTimeout = -1)
	{
		assert(is_resource($hFileHandle));

		$strReadString = "";
		$nStartTime = microtime(true);

		do
		{
			$strPartialReadString = fread($hFileHandle, 4096);
			if($strPartialReadString !== false)
			{
				$strReadString .= $strPartialReadString;
				if(!strlen($strPartialReadString))
					break;
			}
		}
		while($nTimeout === -1 || (microtime(true) - $nStartTime) <= $nTimeout);

		return $strReadString;
	}
		
		
	/**
	 * STDIN pipe index.
	 */
	const STDIN = 0;

	/**
	 * STDOUT pipe index.
	 */
	const STDOUT = 1;

	/**
	 * STDERR pipe index.
	 */
	const STDERR = 2;

	/**
	* The temporary files name prefix.
	*/
	const TEMPORARY_FILE_NAME_PREFIX = "PROCESS_FORKER_";

	/**
	 * Default select timeout.
	 */
	const SELECT_TIMEOUT_DEFAULT_USEC = 1000000;

	/**
	 * Process termination signal.
	 */
	const SIGKILL = 9;
}

