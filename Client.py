import json;
import urllib;
import urllib2;
import hmac;
import hashlib;
import time;
import os;
import base64;
import logging;
from urllib2 import HTTPError;
from JSONRPCException import JSONRPCException;
from JSONRPCBaseException import JSONRPCBaseException;

class Client(object):
    """
    """

    """
    JSON-RPC protocol call ID.
    """
    __nCallID = 0;

    """
    Filter plugins which extend ClientPluginBase.
    """
    __arrFilterPlugins = [];

    """
    JSON-RPC server endpoint URL.
    """
    __strJSONRPCRouterURL = "";

    def __init__(self, strJSONRPCRouterURL, strLogFilePath = "CommunicationLog.log"):
        """
        This is the constructor function. It creates a new instance of Client.
        Example: Client("http://example.ro").

        @param string strJSONRPCRouterURL. The adress of the server.
        @param string strLogFilePath. This is the file path where the info messages should
        be written. It is not mandatory, a file "CommunicationLog.log" is created by default.
        """
        # logging.basicConfig(filename = strLogFilePath, format = "%(asctime)s %(message)s");
        # self.__objLogger = logging.getLogger(__name__);

        self.__strJSONRPCRouterURL = strJSONRPCRouterURL;

    """
    HTTP credentials used for authentication plugins.
    """
    _strHTTPUser = None;
    _strHTTPPassword = None;

    def setHTTPCredentials(self, strUsername, strPassword):
        """
        This is the function used to set the HTTP credentials set.

        @param string strUsername.
        @param string strPassword.
        """
        assert isinstance(strUsername, str);
        assert isinstance(strPassword, str);

        self._strHTTPUser = strUsername;
        self._strHTTPPassword = strPassword;

    def _rpc(self, strFunctionName, arrParams):
        dictRequest = {
            "jsonrpc": "2.0",
            "method": strFunctionName,
            "params": arrParams,
            "id": ++self.__nCallID
        };

        for objFilterPlugin in self.__arrFilterPlugins:
            if objFilterPlugin.beforeJSONEncode(dictRequest) is not None:
                dictRequest = objFilterPlugin.beforeJSONEncode(dictRequest);

        strRequest = json.dumps(dictRequest);
        strEndPointURL = self.__strJSONRPCRouterURL;

        dictHTTPHeaders = {
            "Content-Type": "application/json"
        };

        if self._strHTTPUser is not None and self._strHTTPPassword is not None:
            dictHTTPHeaders["Authorization"] = "Basic " + base64.b64encode(self._strHTTPUser + ":" + self._strHTTPPassword);

        for objFilterPlugin in self.__arrFilterPlugins:
            if objFilterPlugin.afterJSONEncode(strRequest, strEndPointURL, dictHTTPHeaders) is not None:
                strRequest, strEndPointURL, dictHTTPHeaders = objFilterPlugin.afterJSONEncode(strRequest, strEndPointURL, dictHTTPHeaders);

        bErrorMode = False;
        bCalled = False;

        for objFilterPlugin in self.__arrFilterPlugins:
            if objFilterPlugin.makeRequest(bCalled, strRequest, strEndPointURL) is not None:
                strResult = objFilterPlugin.makeRequest(bCalled, strRequest, strEndPointURL);

            if bCalled:
                break;

        if bCalled == False:
            objRequest = urllib2.Request(strEndPointURL, headers = dictHTTPHeaders, data = strRequest);

            try:
                objFile = urllib2.urlopen(objRequest);
                strResult = objFile.read();
            except urllib2.HTTPError, objError:
                bErrorMode = True;
                strResult = objError.read();

        return self.processRAWResponse(strResult, bErrorMode);

    def processRAWResponse(self, strResult, bErrorMode = False):
        """
        This is the function used to decode the received JSON and return its result.
        It is automatically called by _rpc.

        @param string strResult. It represents the received JSON.
        @param boolean bErrMode. Whether or not the received JSON contains errors.

        @return mixed mxResponse["result"]. This is the server response result.
        """
        try:
            mxResponse = None;

            for objFilterPlugin in self.__arrFilterPlugins:
                objFilterPlugin.beforeJSONDecode(strResult);

            try:
                mxResponse = json.loads(strResult);
            except Exception, objError:
                raise JSONRPCException(
                    objError.message + ". RAW response from server: " + strResult, JSONRPCException.PARSE_ERROR
                );

            for objFilterPlugin in self.__arrFilterPlugins:
                objFilterPlugin.afterJSONDecode(strResult, mxResponse);

            if isinstance(mxResponse, dict) == False or (bErrorMode == True and mxResponse.has_key("error") == False):
                raise JSONRPCException(
                    "Invalid response structure. RAW response: " + strResult, JSONRPCException.INTERNAL_ERROR
                );
            elif mxResponse.has_key("result") == True and mxResponse.has_key("error") == False and bErrorMode == False:
                return mxResponse["result"];

            raise JSONRPCException(
                str(mxResponse["error"]["message"]), int(mxResponse["error"]["code"])
            );
        except JSONRPCException, objError:
            for objFilterPlugin in self.__arrFilterPlugins:
                objFilterPlugin.exceptionCatch(objError);

            raise objError;

    def __getattr__(self, strClassAttribute):
        """
        This is a magic function, which facilitates the lookup for Client class attributes.
        In order to be able to call whitelisted server functions, they are defined as class attributes
        through the medium of the function __call.
        If the function is not whitelisted, an exception is thrown.

        @param string strFunctionName. This is the name of the function to be called.

        @return object __call. The new defined function.
        """
        def __call(*tupleParams):
            """
            This is a local function, which is used to define a function in a class attributes
            for Client, based on its name and array of parameters

            @param *tupleParams. It allows you to pass an arbitrary number of parameters, no matter their type.

            @return the result of the _rpc function.
            """
            arrParams = list(tupleParams);
            return self._rpc(strClassAttribute, arrParams);

        return __call;

    def addFilterPlugin(self, objFilterPlugin):
        """
        This function is used to add filter plugins to an instance of Client
        If there is an attempt to add multiple instances of the same filter,
        an exception is thrown.

        @param object objFilterPlugin. The class of this object should extend the
        ClientPluginBase.
        """
        for objFilterPluginExisting in self.__arrFilterPlugins:
            if objFilterPluginExisting.__class__ == objFilterPlugin.__class__:
                raise Exception(
                    "Multiple instances of the same filter is not allowed."
                );

        self.__arrFilterPlugins.append(objFilterPlugin);

    def removeFilterPlugin(self, objFilterPlugin):
        """
        This function is used to remove Client filter plugins.
        If there is an attempt to remove an unregistred filter plugin,
        an exception is thrown.

        @param object objFilterPlugin. The class of this object should extend the
        ClientPluginBase
        """
        nIndex = None;

        for i in range(len(self.__arrFilterPlugins)):
            if objFilterPlugin.__class__ == self.__arrFilterPlugins[i].__class__:
                nIndex = i;
                break;

        if isinstance(nIndex, int) == False:
            raise Exception(
                "Failed to remove filter plugin object, maybe plugin is not registered"
            );

        del self.__arrFilterPlugins[nIndex];

    def rpcFunctions(self):
        """
        This function is used to list all the API functions.
        """
        return self._rpc("rpc.functions", []);

    def rpcReflectionFunction(self, strFunctionName):
        """
        This function is used to return a specific rpcReflectionFunction of the API.

        @param string strFunctionName.
        """
        return self._rpc("rpc.rpcReflectionFunction", [strFunctionName]);

    def rpcReflectionFunctions(self, arrFunctionNames):
        """
        This function is used to return specific rpcReflectionFunctionsof the API.

        @param array arrFunctionNames.
        """
        return self._rpc("rpc.rpcReflectionFunctions", [arrFunctionNames]);
