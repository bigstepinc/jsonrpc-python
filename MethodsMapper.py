import inspect
import json
from JSONRPC_Exception import JSONRPC_Exception

class MethodsMapper(object):
	def __init___(self):
		pass

	"""
	 * @var object
	"""
	_instanceWithAPIMethods = None
		
		
	"""
	 * Associative array with API functions names as keys and method names as values.
	 * 
	 * @var array
	"""
	_dictAPIFunctionsNamesToMethodsNames = []
		
		
	"""
	 * dictAPIFunctionsNamesToMethodsNames can be a dictionary or null.
	 * If null, then all class methods names are mapped to themselves.
	 * 
	 * @param object instanceWithAPIMethods 
	 * @param array dictAPIFunctionsNamesToMethodsNames = None
	"""
	def __init__(self, instanceWithAPIMethods, dictAPIFunctionsNamesToMethodsNames = None):
		if (dictAPIFunctionsNamesToMethodsNames == None):
			for strMethodName in inspect.getmembers(instanceWithAPIMethods.__class__.__name__):
				"""
				 * inspect.getmembers returns a list of 2-tuples with the name of the class
				 * method in the first part of the tuple
				"""
				self._dictAPIFunctionsNamesToMethodsNames[strMethodName[0]] = strMethodName[0]
		else:
			self._validateInstanceHasMethods(instanceWithAPIMethods, dictAPIFunctionsNamesToMethodsNames.values())
			self._dictAPIFunctionsNamesToMethodsNames = dictAPIFunctionsNamesToMethodsNames
		
		self._instanceWithAPIMethods = instanceWithAPIMethods
		
		
	"""
	 * @return object
	"""
	def instanceWithAPIMethods(self):
		return self._instanceWithAPIMethods
		
		
	"""
	 * @return array
	"""
	def arrAPIFunctionsNamesToMethodsNames(self):
		return self._dictAPIFunctionsNamesToMethodsNames
		
		
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
		arrClassMethodNames = [methodName[0] for methodName in inspect.getmembers(instanceWithAPIMethods.__class__.__name__)]
		
		"""This computes the difference between the arrMethodNames and the arrClassMethodNames"""
		setClassMethodNames = set(arrClassMethodNames)
		arrFunctionsNotFoundInClass = [notInClass for notInClass in arrMethodNames if notInClass not in arrClassMethodNames]
		
		if (len(arrFunctionsNotFoundInClass) != 0):
			"""WARNING: Check if it's json.dumps or loads"""
			raise JSONRPC_Exception("Methods " + json.dumps(arrFunctionsNotFoundInClass) + \
									" are not defined in the " + type(instanceWithAPIMethods) + \
									" class.", JSONRPC_Exception.METHOD_NOT_FOUND)
	
