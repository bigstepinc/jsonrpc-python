import json;
import urllib;
import urllib2;
import hmac;
import hashlib;
import time;
import os;
import base64;
import logging;
import threading;
from traceback import format_exc;
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

    """
    """
    __lock = None;

    def __init__(self, strJSONRPCRouterURL, strLogFilePath = "CommunicationLog.log", arrFilterPlugins = []):
        """
        This is the constructor function. It creates a new instance of Client.
        Example: Client("http://example.ro").

        @param string strJSONRPCRouterURL. The adress of the server.
        @param string strLogFilePath. This is the file path where the info messages should
        be written. It is not mandatory, a file "CommunicationLog.log" is created by default.
        @param array arrFilterPlugins
        """
        logging.basicConfig(filename = strLogFilePath, format = "%(asctime)s %(message)s");
        self.__objLogger = logging.getLogger(__name__);

        self.__lock = threading.Lock();

        self.__strJSONRPCRouterURL = strJSONRPCRouterURL;

        for objFilterPlugin in arrFilterPlugins:
            self.__arrFilterPlugins.append(objFilterPlugin);

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
        strRequest, strEndPointURL, dictHTTPHeaders = self.__prepareRequest(strFunctionName, arrParams);

        strResult, bErrorMode = self.__makeRequest(strRequest, strEndPointURL, dictHTTPHeaders);

        return self.processRAWResponse(strResult, bErrorMode);

    def processRAWResponse(self, strResult, bErrorMode = False):
        """
        This is the function used to decode the received JSON and return its result.
        It is automatically called by _rpc.

        @param string strResult. It represents the received JSON.
        @param boolean bErrorMode. Whether or not the received JSON contains errors.

        @return mixed mxResponse["result"]. This is the server response result.
        """
        try:
            bErrorMode, mxResponse = self.__processResponse(strResult, bErrorMode);

            mxResponse = self.__createResponse(strResult, bErrorMode, mxResponse);

            return mxResponse["result"];
        except JSONRPCException, objError:

            """
            Log the initial exception.
            """
            self.__logException(objError);

            for objFilterPlugin in self.__arrFilterPlugins:
                objFilterPlugin.exceptionCatch(objError);

            raise objError;

    def __prepareRequest(self, strFunctionName, arrParams):
        """
        @param string strFunctionName
        @param array arrParams

        @return array strRequest, strEndPointURL, dictHTTPHeaders
        """

        self.__lock.acquire();
        self.__nCallID += 1;
        self.__lock.release();

        dictRequest = {
            "jsonrpc": "2.0",
            "method": strFunctionName,
            "params": arrParams,
            "id": self.__nCallID
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

        return strRequest, strEndPointURL, dictHTTPHeaders;

    def __makeRequest(self, strRequest, strEndPointURL, dictHTTPHeaders):
        """
        @param string strRequest
        @param string strEndPointURL
        @param dictionary dictHTTPHeaders

        @return array strResult, bErrorMode
        """
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

        return strResult, bErrorMode;

    def __processResponse(self, strResult, bErrorMode):
        """
        @param string strResult
        @param boolean bErrorMode

        @return array bErrorMode, mxResponse
        """
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

        return bErrorMode, mxResponse;

    def __createResponse(self, strResult, bErrorMode, mxResponse):
        """
        @param string strResult
        @param boolean bErrorMode
        @param mixed mxResponse

        @return mixed mxResponse
        """
        if isinstance(mxResponse, dict) == False or (bErrorMode == True and mxResponse.has_key("error") == False):
            raise JSONRPCException(
                "Invalid response structure. RAW response: " + strResult, JSONRPCException.INTERNAL_ERROR
            );
        elif mxResponse.has_key("result") == True and mxResponse.has_key("error") == False and bErrorMode == False:
            return mxResponse;

        raise JSONRPCException(
            str(mxResponse["error"]["message"]), int(mxResponse["error"]["code"])
        );

    def __logException(self, exc):
        """
        * Logs an exception.
        """
        dictExc = self.__formatException(exc, False);
        self.__objLogger.exception(dictExc["message"]);

    def __formatException(self, exc, bIncludeStackTrace = True):
        """
        Formats an exception as an associative array with message and code keys properly set.
        """
        nCode = JSONRPCException.INTERNAL_ERROR;

        if isinstance(exc, JSONRPCBaseException):
            strStrackTrace = exc.getStackTrace();
            strMessage = exc.getMessage();
            nCode = exc.getCode();
        else:
            strMessage = str(exc);
            strStrackTrace = format_exc();

        strMessage = "Message: \"%s\" Code: %d" % (strMessage, nCode);
        if bIncludeStackTrace:
            strMessage = "%s\n\n%s" % (strMessage, strStrackTrace);

        return {
            "message": strMessage,
            "code": nCode
        };

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
