from ...ClientFilterBase import JSONRPC_client_filter_plugin_base
from JSONRPC_Exception import JSONRPC_Exception

class BSIExceptionFilter(JSONRPC_client_filter_plugin_base):

	def exceptionCatch(self, exception):

		if exception.getCode() >= 0:
			raise BSI_Exception(exception.message, exception.code)
		else:
			raise exception
