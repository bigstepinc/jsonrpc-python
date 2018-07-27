import json
from time import strftime, localtime
from jsonrpc2_base.plugins.client.client_plugin_base import ClientPluginBase
from __future__ import print_function

class DebugLogger(ClientPluginBase):
    """
    JSONRPC 2.0 client plugin.
    Adds authentication and signed request expiration for the JSONRPC ResselerDomainsAPI.
    Also translates thrown exceptions.
    """

    bLogType = True

    def __init__(self, bLogType, strLogPath=""):
        """
        @param boolean bLogType
        @param string strLogPath
        """
        self.bLogType = bLogType

        if bLogType == False:
            if strLogPath != "":
                self.hFile = open(strLogPath, "a")
            else:
                raise Exception("No log path specified.")

    def beforeJSONDecode(self, strJSONResponse):
        """
        @param string strJSONResponse
        """
        strOutput = strJSONResponse
        objDecoded = json.loads(strOutput)
        strOutput = "Received response at: " + strftime("%Y-%m-%d %X", localtime()) + "\n" + json.dumps(objDecoded,
                                                                                                        sort_keys=True,
                                                                                                        indent=4) + "\n"
        if self.bLogType == True:
            print(strOutput)
        else:
            self.hFile.write(strOutput + "\n")

    def afterJSONEncode(self, strJSONRequest, strEndPointURL, dictHTTPHeaders):
        """
        @param string strJSONRequest
        @param string strEndPointURL
        @param object dictHTTPHeaders
        """
        strOutput = strJSONRequest
        objDecoded = json.loads(strOutput)
        strOutput = "Sent request at: " + strftime("%Y-%m-%d %X", localtime()) + "\n" + json.dumps(objDecoded,
                                                                                                   sort_keys=True,
                                                                                                   indent=4) + "\n"
        if self.bLogType == True:
            print(strOutput)
        else:
            self.hFile.write(strOutput + "\n")
