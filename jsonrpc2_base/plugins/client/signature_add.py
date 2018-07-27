import hashlib
import hmac
import time
import urllib

from jsonrpc2_base.plugins.client.client_plugin_base import ClientPluginBase

class SignatureAdd(ClientPluginBase):
    """
    JSON-RPC 2.0 client plugin.
    Adds authentication and signed request expiration for the JSONRPC ResellerDomainsAPI.
    Also translates thrown exceptions.
    """

    """
    Private key used for hashed messages sent to the server
    """
    strAPIKey = ""

    """
    Extra URL variables
    """
    dictExtraURLVariables = {}

    """
    Private key used for hashed messages sent to the server
    """
    strKeyMetaData = ""

    def __init__(self, strKey, dictExtraURLVariables):
        """
        This is the constructor function. It creates a new instance of SignatureAdd
        Example: SignatureAdd("secretKey")

        @param string strKey. The private key used for hashed messages sent to the server.
        @param object dictExtraURLVariables.
        """
        self.strAPIKey = strKey
        self.dictExtraURLVariables = dictExtraURLVariables
        self.getKeyMetaData()

    def getKeyMetaData(self):
        """
        """
        strKEYSplit = self.strAPIKey.split(":", 2)
        if (strKEYSplit.__len__() == 1):
            self.strKeyMetaData = None
        else:
            self.strKeyMetaData = strKEYSplit[0]

    def beforeJSONEncode(self, dictRequest):
        """
        This function sets an uptime for the request.

        @param object dictRequest

        @return object dictRequest
        """
        dictRequest["expires"] = int(time.time() + 86400)
        return dictRequest

    def afterJSONEncode(self, strJSONRequest, strEndPointURL, dictHTTPHeaders):
        """
        This function is used for authentication. It alters the endpoint URL such that it contains
        a specific signature.

        @param string strJSONRequest
        @param string strEndPointURL
        @param object dictHTTPHeaders

        @return array strJSONRequest, strEndPointURL, dictHTTPHeaders
        """
        strVerifyHash = hmac.new(self.strAPIKey.encode("utf-8"), strJSONRequest, hashlib.md5).hexdigest()

        if (self.strKeyMetaData != None):
            strVerifyHash = self.strKeyMetaData + ":" + strVerifyHash

        if (strEndPointURL.find("?") != -1):
            strEndPointURL += "&"
        else:
            strEndPointURL += "?"

        if strEndPointURL.find("?verify") == -1:
            strEndPointURL += "verify=" + urllib.quote(strVerifyHash)

        for key, value in self.dictExtraURLVariables.items():
            value = str(value)
            strEndPointURL += "&" + urllib.quote(key) + "=" + urllib.quote(value)

        return strJSONRequest, strEndPointURL, dictHTTPHeaders
