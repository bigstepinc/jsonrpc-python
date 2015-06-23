"""
* JSON-RPC 2.0 client filter plugin.
* Adds authentication and signed request expiration for the JSONRPC ResellerDomainsAPI.
* Also translates thrown exceptions.
"""

"""THIS IS NOT FULLY IMPLEMENTED"""
"""It does not support output to browser"""


import json
import datetime
import sys
from time import strftime, localtime
from ...ClientFilterBase import JSONRPC_ClientFilterBase

class DebugLogger(JSONRPC_ClientFilterBase):

	LOG_AUTO = 0
	LOG_TO_CONSOLE = 1
	LOG_TO_FILE = 2
	LOG_TO_BROWSER = 3

	nLogType = 0
	strLogPath = "output"



	def __init__(self, bLogType, strLogPath = "console"):

		self.nLogType = nLogType

		"""TODO"""
		if (nLogType == LOG_TO_FILE):
			if strLogPath != "":
				self.hFile = open(strLogPath, "a")
			else:
				raise Exception("No log path specified")
		else if (nLogType == LOG_TO_CONSOLE):
			self.strLogPath = "console"
		else:
			raise Exception("Log to browser not supported!")



	def beforeJSONDecode(self, strJSONResponse):

		strOutput = strJSONResponse
		objDecoded = json.loads(strOutput)
		strOutput = "Received response at: " + strftime("%Y-%m-%d %X", localtime()) + "\n" + json.dumps(objDecoded, sort_keys=True, indent=4) + "\n"

		if self.nLogType == LOG_TO_CONSOLE:
			print strOutput
		else:
			self.hFile.write(strOutput + "\n")




	def afterJSONEncode(self, strJSONRequest, strEndpointURL, dictHTTPHeaders):

		strOutput = strJSONRequest
		if (strOutput == "console"):
			objDecoded = json.loads(sys.stdin)
		else:
			objDecoded = json.loads(strOutput)
		strOutput = "Sent request at: " + strftime("%Y-%m-%d %X", localtime()) + "\n" + json.dumps(objDecoded, sort_keys=True, indent=4) + "\n"
		
		if self.nLogType == LOG_TO_CONSOLE:
			print strOutput
		else:
			self.hFile.write(strOutput + "\n")


	"""TODO"""
	def formatJSON(self, strJSON, nIndentLevel = 0, strTabCharacter = "	"):
		return

	"""TODO"""
	def logger(string):
		return



		
