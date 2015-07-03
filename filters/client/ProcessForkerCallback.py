"""TODO: imports"""
"""
 * Callback class that retains the additional parameters of the call besides the call result. 
 * It is used by the ProcessForker plugin.
"""
class ProcessForkerCallback(object):
	"""
	 * @var array The additional parameters of the callback besides the call result.
	"""
	"""WARNING: Careful with this"""
	_dictParameters = None
		
		
	"""
	 * @var callable Callback function
	"""
	_callableFunction = None
		
		
	"""
	 * @var callback response
	"""
	_tupResponse = None
				
		
	"""
	 * Class constructor that initializes the callback function and parameters.
	 *
	 * @param callable callableFunction The callback function to be called.
	 * @param array dictParams The callback function parameters.
	 *
	 * @return None.
	"""
	"""WARNING: [] vs None"""
	def __init__(self, callableFunction, dictParameters = None):
		"""WARNING: You may want to encapsulate this in try...except"""
		if (not isinstance(callableFunction, callable)):
			raise Exception("Invalid callback function. The callback function must be callable.")
		
		self._callableFunction = callableFunction
		self._dictParameters = dictParameters
		
		
	"""
	 * Calls the callback function with the given parameters and the provided result.
	 *
	 * @param tuple tupResult The result of the function call.
	 *
	 * @return None.
	"""
	def call(self, tupResult):
		"""TODO: This looks wrong"""
		"""TODO: call_user_func_array"""
		call_user_func_array(
			self._callableFunction,
			list(tupResult) + list(self._dictParameters))

		self._tupResponse = tupResult
		

	"""
	 * Is returning callback response
	 *
	 * @return tuple.
	"""
	def getResponse(self):
		return self._tupResponse