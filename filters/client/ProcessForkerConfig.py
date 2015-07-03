"""TODO: imports"""
"""
 * Config class that retains the configuration parameters for each call. 
"""
class ProcessForkerConfig(object):
{
	"""
	 * @var bool _bRunAsPrivilegedUser Determines the process forker plugin to use
	 * sudo for the call.
	"""
	_bRunAsPrivilegedUser = None
		
	"""TODO: Change documentation"""
	"""
	 * @var float _fTimeout Determines the timeout the process forker plugin will use for
	 * the call. The timeout format should be consistent with the one returned by  microtime(true).
	"""
	_fTimeout = None
		
	
	"""
	 * Class constructor that initializes the config parameters.
	 *
	 * @param bool bRunAsPrivilegedUser. Determines the process forker plugin to use
	 * sudo for the call.
	 * @param int nTimeout. Determines the timeout the process forker plugin will use for
	 * the call. The timeout is in microseconds.
	 *
	 * @return None.
	"""
	"""WARNING: Removed & reference"""
	def __init__(self, bRunAsPrivilegedUser = False, nTimeout = -1):
		self._bRunAsPrivilegedUser = bRunAsPrivilegedUser
		if (nTimeout >= 0):
			self._fTimeout = nTimeout * pow(10, -6) 
		else:
			self._fTimeout = -1
		
	"""
	 * @return bool. Run with sudo or not.
	"""
	def runAsPrivilegedUser(self):
		return self._bRunAsPrivilegedUser
		
	"""
	 * @return float. The timeout of the call.
	"""
	def getTimeout(self):
		return self._fTimeout;