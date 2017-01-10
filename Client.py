import json;
import urllib2;

import logging;
import threading;

from traceback import format_exc;

import HeaderFactory
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
    Used for locking variables in case of multithreading.
    """
    __lock = None;

    """
    HTTP credentials used for authentication plugins.
    """
    __strHTTPUser = None;
    __strHTTPPassword = None;


    def __init__(self, dictParams, arrFilterPlugins = []):
        """
        This is the constructor function. It creates a new instance of Client.
        Example: Client("http://example.ro").

        @param object dictParams. It is used for reference return for multiple variables,
        which can be retrieved using specific keys
            - "strJSONRPCRouterURL". The adress of the server.
            - "strLogFilePath". This is the file path where the info messages should
            be written. A file "CommunicationLog.log" is created by default.
            - "strUsername". Used to set the HTTP credentials set.
            - "strPassword". Used to set the HTtp credentials set.
        @param array arrFilterPlugins
        """
        if not "strJSONRPCRouterURL" in dictParams:
            raise JSONRPCException(
                "The strJSONRPCRouterURL property must be set.", JSONRPCException.INVALID_PARAMS
            );
        self.__strJSONRPCRouterURL = dictParams["strJSONRPCRouterURL"];

        if "strUsername" in dictParams:
            self.__strHTTPUser = dictParams["strUsername"];
        if "strPassword" in dictParams:
            self.__strHTTPPassword = dictParams["strPassword"];
        if not "strLogFilePath" in dictParams:
            dictParams["strLogFilePath"] = "CommunicationLog.log";

        if not len(set(arrFilterPlugins)) == len(arrFilterPlugins):
            raise JSONRPCException(
                "The client filter plugin list contains duplicates.", JSONRPCException.INVALID_PARAMS
            );
        self.__arrFilterPlugins = list(arrFilterPlugins);

        logging.basicConfig(filename = dictParams["strLogFilePath"], format = "%(asctime)s %(message)s");
        self.__objLogger = logging.getLogger(__name__);

        self.__lock = threading.Lock();


    def _rpc(self, strFunctionName, arrParams):
        """
        @param string strFunctionName
        @param array arrParams

        @return processRAWResponse. The function used to decode the received JSON.
        """
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
        nCallID = self.__nCallID;
        self.__nCallID += 1;
        self.__lock.release();

        dictRequest = {
            "jsonrpc": "2.0",
            "method": strFunctionName,
            "params": arrParams,
            "id": nCallID
        };

        for objFilterPlugin in self.__arrFilterPlugins:
            if objFilterPlugin.beforeJSONEncode(dictRequest) is not None:
                dictRequest = objFilterPlugin.beforeJSONEncode(dictRequest);

        strRequest = json.dumps(dictRequest);
        strEndPointURL = self.__strJSONRPCRouterURL;

        headerFactory = HeaderFactory()
        dictHTTPHeaders = headerFactory.create(sUser= self.__strHTTPUser, sPassword= self.__strHTTPPassword,
                                                 sContentType= "application/json")

        for objFilterPlugin in self.__arrFilterPlugins:
            if objFilterPlugin.afterJSONEncode(strRequest, strEndPointURL, dictHTTPHeaders) is not None:
                strRequest, strEndPointURL, dictHTTPHeaders = objFilterPlugin.afterJSONEncode(strRequest, strEndPointURL, dictHTTPHeaders);

        return strRequest, strEndPointURL, dictHTTPHeaders;


    def __makeRequest(self, strRequest, strEndPointURL, dictHTTPHeaders):
        """
        @param string strRequest
        @param string strEndPointURL
        @param object dictHTTPHeaders

        @return array strResult, bErrorMode
        """
        bErrorMode = False;
        bCalled = False;

        for objFilterPlugin in self.__arrFilterPlugins:
            if objFilterPlugin.makeRequest(bCalled, strRequest, strEndPointURL) is not None:
                bCalled, strResult, strEndPointURL = objFilterPlugin.makeRequest(bCalled, strRequest, strEndPointURL);

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


    def __logException(self, exc):
        """
        Logs an exception.

        @param exception exc
        """
        dictExc = self.__formatException(exc, False);
        self.__objLogger.exception(dictExc["message"]);


    def __formatException(self, exc, bIncludeStackTrace = True):
        """
        Formats an exception as an associative array with message and code keys properly set.

        @param exception exc
        @param boolean bIncludeStackTrace

        @return a dictionary with message and code keys properly set.
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
        @return all API functions
        """
        return self._rpc("rpc.functions", []);


    def rpcReflectionFunction(self, strFunctionName):
        """
        @param string strFunctionName.

        @return a specific rpcReflectionFunction of the API
        """
        return self._rpc("rpc.rpcReflectionFunction", [strFunctionName]);


    def rpcReflectionFunctions(self, arrFunctionNames):
        """
        @param array arrFunctionNames.

        @return specific rpcReflectionFunctions of the API
        """
        return self._rpc("rpc.rpcReflectionFunctions", [arrFunctionNames]);