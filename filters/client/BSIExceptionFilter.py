from ...ClientFilterBase import JSONRPC_client_filter_plugin_base
from BSI.BSI_Exception import BSI_Exception

class BSIExceptionFilter(JSONRPC_client_filter_plugin_base):

	def exceptionCatch(self, exception):

		if exception.nCode >= 0:
			raise BSI_Exception(exception.strMessage, exception.nCode)
		else:
			raise exception
