class MethodsMapper(object):
	def __init___(self):

	"""
	 * @var object
	"""
	_instanceWithAPIMethods = None
		
		
	"""
	 * Associative array with API functions names as keys and method names as values.
	 * 
	 * @var array
	"""
	_arrAPIFunctionsNamesToMethodsNames = []
		
		
	"""
	 * arrAPIFunctionsNamesToMethodsNames can be a dictionary or null.
	 * If null, then all class methods names are mapped to themselves.
	 * 
	 * @param object instanceWithAPIMethods 
	 * @param array arrAPIFunctionsNamesToMethodsNames = None
	"""
	def __construct(self, instanceWithAPIMethods, arrAPIFunctionsNamesToMethodsNames = None):
		if (arrAPIFunctionsNamesToMethodsNames == None):
			"""TODO: get_class_methods"""
			for (strMethodName in get_class_methods(type(instanceWithAPIMethods))):
				self._arrAPIFunctionsNamesToMethodsNames[strMethodName] = strMethodName
		else:
			"""TODO: array_values"""
			self._validateInstanceHasMethods(instanceWithAPIMethods, array_values(arrAPIFunctionsNamesToMethodsNames))
			self._arrAPIFunctionsNamesToMethodsNames = arrAPIFunctionsNamesToMethodsNames
		
		self._instanceWithAPIMethods = instanceWithAPIMethods
		
		
	"""
	 * @return object
	"""
	def instanceWithAPIMethods(self):
		return self._instanceWithAPIMethods
		
		
	"""TODO: CHeck if it's indeed an array at return"""
	"""
	 * @return array
	"""
	def arrAPIFunctionsNamesToMethodsNames(self):
		return self._arrAPIFunctionsNamesToMethodsNames
		
		
	"""TODO: Check documentation"""
	"""
	 * Makes sure arrMethodNames are defined on instanceWithAPIMethods's class.
	 * 
	 * @param object instanceWithAPIMethods 
	 * @param array arrMethodNames 
	 * 
	 * @throws JSONRPC_Exception 
	 * @return None
	"""
	def _validateInstanceHasMethods(self, instanceWithAPIMethods, arrMethodNames):
		"""TODO: Find out get_class_methods"""
		arrClassMethodNames = get_class_methods(type(instanceWithAPIMethods))
		
		"""TODO: array_diff. Guess it's a minus or something"""
		arrFunctionsNotFoundInClass = array_diff(arrMethodNames, arrClassMethodNames)
		
		if (len(arrFunctionsNotFoundInClass) != 0):
			"""Check if it's json.dumps or loads"""
			raise JSONRPC_Exception("Methods " + json.dumps(arrFunctionsNotFoundInClass) + \
									" are not defined in the " + type(instanceWithAPIMethods) + \
									" class.", JSONRPC_Exception.METHOD_NOT_FOUND)
	
