from future.standard_library import hooks
with hooks():
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError

import json
import logging
import threading
from traceback import format_exc

from jsonrpc2_base.jsonrpc_base_exception import JSONRPCBaseException
from jsonrpc2_base.jsonrpc_exception import JSONRPCException
from jsonrpc2_base.header_factory import HeaderFactory

class Client(object):
    """
    """

    """
    JSON-RPC protocol call ID.
    """
    __nCallID = 0

    """
    Filter plugins which extend ClientPluginBase.
    """
    __arrFilterPlugins = []

    """
    JSON-RPC server endpoint URL.
    """
    __strJSONRPCRouterURL = ""

    """
    Used for locking variables in case of multithreading.
    """
    __lock = None

    """
    HTTP credentials used for authentication plugins.
    """
    __strHTTPUser = None
    __strHTTPPassword = None

    def __init__(self, dictParams, arrFilterPlugins=[]):
        """
        This is the constructor function. It creates a new instance of client.
        Example: client("http://example.ro").

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
            )
        self.__strJSONRPCRouterURL = dictParams["strJSONRPCRouterURL"]

        if "strUsername" in dictParams:
            self.__strHTTPUser = dictParams["strUsername"]
        if "strPassword" in dictParams:
            self.__strHTTPPassword = dictParams["strPassword"]
        if not "strLogFilePath" in dictParams:
            dictParams["strLogFilePath"] = "CommunicationLog.log"

        if not len(set(arrFilterPlugins)) == len(arrFilterPlugins):
            raise JSONRPCException(
                "The client filter plugin list contains duplicates.", JSONRPCException.INVALID_PARAMS
            )
        self.__arrFilterPlugins = list(arrFilterPlugins)

        logging.basicConfig(filename=dictParams["strLogFilePath"], format="%(asctime)s %(message)s")
        self.__objLogger = logging.getLogger(__name__)

        self.__lock = threading.Lock()

    def rpc(self, strFunctionName, arrParams):
        """
        @param string strFunctionName
        @param array arrParams

        @return processRAWResponse. The function used to decode the received JSON.
        """
        strRequest, strEndPointURL, dictHTTPHeaders = self._prepareRequest(strFunctionName, arrParams)
        strResult, bErrorMode = self._makeRequest(strRequest, strEndPointURL, dictHTTPHeaders)

        return self.processRAWResponse(strResult, bErrorMode)

    def processRAWResponse(self, strResult, bErrorMode=False):
        """
        This is the function used to decode the received JSON and return its result.
        It is automatically called by rpc.

        @param string strResult. It represents the received JSON.
        @param boolean bErrorMode. Whether or not the received JSON contains errors.

        @return mixed mxResponse["result"]. This is the server response result.
        """
        try:
            mxResponse = None

            for objFilterPlugin in self.__arrFilterPlugins:
                objFilterPlugin.beforeJSONDecode(strResult)

            try:
                mxResponse = json.loads(strResult)
            except ValueError as objError:
                raise JSONRPCException(
                    str(objError) + ". RAW response from server: " + strResult, JSONRPCException.PARSE_ERROR
                )

            for objFilterPlugin in self.__arrFilterPlugins:
                objFilterPlugin.afterJSONDecode(strResult, mxResponse)

            if isinstance(mxResponse, dict) == False or (bErrorMode == True and mxResponse.has_key("error") == False):
                raise JSONRPCException(
                    "Invalid response structure. RAW response: " + strResult, JSONRPCException.INTERNAL_ERROR
                )
            elif mxResponse.has_key("result") == True and mxResponse.has_key("error") == False and bErrorMode == False:
                return mxResponse["result"]

            raise JSONRPCException(
                str(mxResponse["error"]["message"]), int(mxResponse["error"]["code"])
            )
        except JSONRPCException as objError:
            """
            Log the initial exception.
            """
            self._logException(objError)

            for objFilterPlugin in self.__arrFilterPlugins:
                objFilterPlugin.exceptionCatch(objError)

            raise objError

    def _prepareRequest(self, strFunctionName, arrParams):
        """
        @param string strFunctionName
        @param array arrParams

        @return array strRequest, strEndPointURL, dictHTTPHeaders
        """
        self.__lock.acquire()
        nCallID = self.__nCallID
        self.__nCallID += 1
        self.__lock.release()

        dictRequest = {
            "jsonrpc": "2.0",
            "method": strFunctionName,
            "params": arrParams,
            "id": nCallID
        }

        for objFilterPlugin in self.__arrFilterPlugins:
            if objFilterPlugin.beforeJSONEncode(dictRequest) is not None:
                dictRequest = objFilterPlugin.beforeJSONEncode(dictRequest)

        strRequest = json.dumps(dictRequest)
        strEndPointURL = self.__strJSONRPCRouterURL

        headerFactory = HeaderFactory()
        dictHTTPHeaders = headerFactory.create(self.__strHTTPUser, self.__strHTTPPassword, "application/json")

        for objFilterPlugin in self.__arrFilterPlugins:
            if objFilterPlugin.afterJSONEncode(strRequest, strEndPointURL, dictHTTPHeaders) is not None:
                strRequest, strEndPointURL, dictHTTPHeaders = objFilterPlugin.afterJSONEncode(strRequest,
                                                                                              strEndPointURL,
                                                                                              dictHTTPHeaders)

        return strRequest, strEndPointURL, dictHTTPHeaders

    def _makeRequest(self, strRequest, strEndPointURL, dictHTTPHeaders):
        """
        @param string strRequest
        @param string strEndPointURL
        @param object dictHTTPHeaders

        @return array strResult, bErrorMode
        """
        bErrorMode = False
        bCalled = False

        for objFilterPlugin in self.__arrFilterPlugins:
            if objFilterPlugin.makeRequest(bCalled, strRequest, strEndPointURL) is not None:
                bCalled, strResult, strEndPointURL = objFilterPlugin.makeRequest(bCalled, strRequest, strEndPointURL)

            if bCalled:
                break

        if bCalled == False:
            objRequest = Request(strEndPointURL, headers=dictHTTPHeaders, data=strRequest.encode("utf-8"))

            try:
                objFile = urlopen(objRequest)
                strResult = objFile.read()
            except HTTPError as objError:
                bErrorMode = True
                strResult = objError.read()

        return strResult.decode("utf-8"), bErrorMode

    def _logException(self, exc):
        """
        Logs an exception.

        @param exception exc
        """
        dictExc = self._formatException(exc, False)
        self.__objLogger.exception(dictExc["message"])

    def _formatException(self, exc, bIncludeStackTrace=True):
        """
        Formats an exception as an associative array with message and code keys properly set.

        @param exception exc
        @param boolean bIncludeStackTrace

        @return a dictionary with message and code keys properly set.
        """
        nCode = JSONRPCException.INTERNAL_ERROR

        if isinstance(exc, JSONRPCBaseException):
            strStrackTrace = exc.getStackTrace()
            strMessage = exc.getMessage()
            nCode = exc.getCode()
        else:
            strMessage = str(exc)
            strStrackTrace = format_exc()

        strMessage = "Message: \"%s\" Code: %d" % (strMessage, nCode)
        if bIncludeStackTrace:
            strMessage = "%s\n\n%s" % (strMessage, strStrackTrace)

        return {
            "message": strMessage,
            "code": nCode
        }

    def __getattr__(self, strClassAttribute):
        """
        This is a magic function, which facilitates the lookup for client class attributes.
        In order to be able to call whitelisted server functions, they are defined as class attributes
        through the medium of the function _call.
        If the function is not whitelisted, an exception is thrown.

        @param string strFunctionName. This is the name of the function to be called.

        @return object _call. The new defined function.
        """

        def _call(*tupleParams):
            """
            This is a local function, which is used to define a function in a class attributes
            for client, based on its name and array of parameters

            @param *tupleParams. It allows you to pass an arbitrary number of parameters, no matter their type.

            @return the result of the rpc function.
            """
            arrParams = list(tupleParams)
            return self.rpc(strClassAttribute, arrParams)

        return _call

    def rpcFunctions(self):
        """
        @return all API functions
        """
        return self.rpc("rpc.functions", [])

    def rpcReflectionFunction(self, strFunctionName):
        """
        @param string strFunctionName.

        @return a specific rpcReflectionFunction of the API
        """
        return self.rpc("rpc.rpcReflectionFunction", [strFunctionName])

    def rpcReflectionFunctions(self, arrFunctionNames):
        """
        @param array arrFunctionNames.

        @return specific rpcReflectionFunctions of the API
        """
        return self.rpc("rpc.rpcReflectionFunctions", [arrFunctionNames])
