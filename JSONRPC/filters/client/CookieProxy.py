"""TODO: imports"""
from ...ClientFilterBase import JSONRPC_ClientFilterBase

"""
 * JSON-RPC 2.0 client filter plugin.
 * Sets the cookies from the response from the server to the browser.
"""
class CookieProxy(ClientFilterBase):
	"""
	 * The cookies names needed to be set. 
	"""
	_arrCookieNames = []

	"""
	 * Allow all cookies flag. If this is true, then _arrCookieNames is ignored.
	"""
	_bAllowAllCookies = False


	"""
	 * Instance of the client.
	 * @type JSONRPC_Client
	"""
	_client = None


	"""TODO: Check argument list [] vs None"""
	def __init__(self, client, arrCookieNames = [], bAllowAllCookies = False):
		self._arrCookieNames = arrCookieNames
		self._bAllowAllCookies = bAllowAllCookies
		self._client = client

	"""TODO: Warning: removed & reference"""
	def afterJSONEncode(self, strJSONRequest, strEndpointURL, arrHTTPHeaders):
		for strCookieName, strCookieValue in _COOKIE:
			"""TODO: cookie"""
			if (self._cookieNameValid(strCookieName)):
				self._client.addCookie(strCookieName, strCookieValue)


	def _cookieNameValid(self, strCookieName):
		if (self._bAllowAllCookies):
			bValidCookieName = True
		else: 
			if (strCookieName in self._arrCookieNames):
				bValidCookieName = True
			else:
				bValidCookieName = False

		return bValidCookieName


	"""WARNING: Removed & reference"""
	def beforeJSONDecode(self, strJSONResponse):
		"""TODO: get type of arrHTTPResponseHeaders"""
		"""TODO: Check type consistency"""
		arrHTTPResponseHeaders = self._client.getHTTPHeaders()

		for arrHTTPResponseHeader in arrHTTPResponseHeaders: 
			if (arrHTTPResponseHeader["name"] == "Set-Cookie"):

				dictSetCookieParams = arrHTTPResponseHeader["value"].split("; ")	
				#the first part of the Set-Cookie represents the name and the value of the cookie
					
				strCookieName, strCookieValue = dictSetCookieParams.split("=").pop()
				if (self._cookieNameValid(strCookieName)):
					arrCookieAttributes = []
					for strSetCookieParams in dictSetCookieParams: 
						dictParams = strSetCookieParams.split("=")
						if (len(dictParams) == 2):
							"""TODO: this doesn't look good"""
							arrCookieAttributes[dictParams[0]] = dictParams[1]
						else:
							arrCookieAttributes.append(arrParams[0])

					"""Set parameters for setcookie"""
					if ("expires" in arrCookieAttributes):
						"""TODO: time"""
						expiryDate = strtotime(arrCookieAttributes["expires"])
					else:
						expiryDate = 0

					if ("path" in arrCookieAttributes):
						path = arrCookieAttributes["path"]
					else:
						path = ""

					if ("domain" in arrCookieAttributes):
						domain = arrCookieAttributes["domain"]
					else:
						domain = ""

					"""TODO: setcookie"""
					setcookie(
						strCookieName,
						strCookieValue,
						expiryDate,
						path,
						domain,
						"secure" in arrCookieAttributes,
						"HttpOnly" in arrCookieAttributes
					)
					"""TODO: _COOKIE"""
					_COOKIE[strCookieName] = strCookieValue
					self._client.addCookie(strCookieName, strCookieValue)
				