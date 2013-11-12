"""
* JSON-RPC 2.0 client filter plugin.
* Adds authentication and signed request expiration for the JSONRPC ResellerDomainsAPI.
* Also translates thrown exceptions.
"""
import json
import datetime
from time import strftime, localtime
from ...ClientFilterBase import JSONRPC_client_filter_plugin_base

class DebugLogger(JSONRPC_client_filter_plugin_base):

	LOG_TO_CONSOLE = True
	LOG_TO_FILE = False

	bLogType = True



	def __init__(self, bLogType, strLogPath = ""):

		self.bLogType = bLogType

		if bLogType == False:
			if strLogPath != "":
				self.hFile = open(strLogPath, "a")
			else:
				raise Exception("No log path specified")



	def beforeJSONDecode(self, dictFilterParams):

		strOutput = dictFilterParams["strJSONResponse"]
		objDecoded = json.loads(strOutput)
		strOutput = "Received response at: " + strftime("%Y-%m-%d %X", localtime()) + "\n" + json.dumps(objDecoded, sort_keys=True, indent=4) + "\n"

		if self.bLogType == True:
			print strOutput
		else:
			self.hFile.write(strOutput + "\n")




	def afterJSONEncode(self, dictFilterParams):

		strOutput = dictFilterParams["strJSONRequest"]
		objDecoded = json.loads(strOutput)
		strOutput = "Sent request at: " + strftime("%Y-%m-%d %X", localtime()) + "\n" + json.dumps(objDecoded, sort_keys=True, indent=4) + "\n"
		
		if self.bLogType == True:
			print strOutput
		else:
			self.hFile.write(strOutput + "\n")



		
