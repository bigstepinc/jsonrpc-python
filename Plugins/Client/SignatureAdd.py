import hmac;
import json;
import urllib2;
import urllib;
import sys;
import hashlib;
import time;
from ClientPluginBase import ClientPluginBase;
from pprint import pprint;

class SignatureAdd(ClientPluginBase):
    """
    JSON-RPC 2.0 client plugin.
    Adds authentication and signed request expiration for the JSONRPC ResellerDomainsAPI.
    Also translates thrown exceptions.
    """

    """
    Private key used for hashed messages sent to the server
    """
    strAPIKey = "";

    """
    Extra URL variables
    """
    dictExtraURLVariables = {};

    """
    Private key used for hashed messages sent to the server
    """
    strKeyMetaData = "";

    def __init__(self, strKey, dictExtraURLVariables):
        """
        This is the constructor function. It creates a new instance of SignatureAdd
        Example: SignatureAdd("secretKey");

        @param string strKey. The private key used for hashed messages sent to the server.
        @param dictionary dictExtraURLVariables.
        """
        self.strAPIKey = strKey;
        self.dictExtraURLVariables = dictExtraURLVariables;
        self.getKeyMetaData();

    def getKeyMetaData(self):
        """
        """
        strKEYSplit = self.strAPIKey.split(":", 2);
        if (strKEYSplit.__len__() == 1):
            self.strKeyMetaData = None;
        else:
            self.strKeyMetaData = strKEYSplit[0];

    def beforeJSONEncode(self, dictFilterParams):
        """
        This function sets an uptime for the request.

        @param dictionary dictFilterParams. It is used for reference return for multiple variables,
        which can be retrieved using specific keys
        - "dictRequest"

        @return dictionary dictFilterParams
        """
        dictFilterParams["dictRequest"]["expires"] = int(time.time() + 86400);
        return dictFilterParams;

    def afterJSONEncode(self, dictFilterParams):
        """
        This function is used for authentication. It alters the Endpoint URL such that it contains
        a specific signature.

        @param dictionary dictFilterParams. It is used for reference return for multiple variables,
        which can be retrieved using specific keys
        - "strJSONRequest"
        - "strEndPointURL"
        - "dictHTTPHeaders"

        @return dictionary dictFilterParams
        """
        strVerifyHash = hmac.new(self.strAPIKey, dictFilterParams["strJSONRequest"], hashlib.md5).hexdigest();

        if (self.strKeyMetaData != None):
            strVerifyHash = self.strKeyMetaData + ":" + strVerifyHash;

        if (dictFilterParams["strEndPointURL"].find("?") != -1):
            dictFilterParams["strEndPointURL"] += "&";
        else:
            dictFilterParams["strEndPointURL"] += "?";

        if dictFilterParams["strEndPointURL"].find("?verify") == -1:
            dictFilterParams["strEndPointURL"] += "verify=" + urllib.quote(strVerifyHash);

        for key, value in self.dictExtraURLVariables.items():
            value = str(value);
            dictFilterParams["strEndPointURL"] += "&" + urllib.quote(key) + "=" + urllib.quote(value);

        return dictFilterParams;
