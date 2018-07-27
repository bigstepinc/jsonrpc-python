import json
import logging
from traceback import format_exc
from six import string_types
from builtins import input

from jsonrpc2_base.jsonrpc_base_exception import JSONRPCBaseException
from jsonrpc2_base.jsonrpc_exception import JSONRPCException
from jsonrpc2_base.plugins.server.reflection_plugin import ReflectionPlugin
from jsonrpc2_base.method_mapper import MethodMapper

class Server(object):
    """
    """

    """
    The version of the JSONRPC.
    """
    __JSONRPC_VERSION = "2.0"

    """
    The name of the logger.
    """
    __objLogger = None

    """
    plugins which extend ServerPluginBase.
    """
    __arrPlugins = []

    """
    Object of MethodMapper class.
    """
    __objMethodMapper = None

    """
    Object of ReflectionPlugin class.
    """
    __objReflectionPlugin = None

    """
    """
    bAuthenticated = False  # We need to modify the Authentication

    """
    """
    bAuthorized = False  # We need to modify the Authorization

    def __init__(self, dictParams, arrPlugins=[]):
        """
        Class constructor.

        @param object dictParams. It is used for reference return for multiple variables,
        which can be retrieved using specific keys
            - "strLogFilePath"
            - "objMethodMapper"
        @param array arrPlugins
        """
        assert isinstance(dictParams["objMethodMapper"], MethodMapper), "Invalid method mapper."
        self.__objMethodMapper = dictParams["objMethodMapper"]
        if not "strLogFilePath" in dictParams:
            dictParams["strLogFilePath"] = "JSONRPC.log"

        self.__objReflectionPlugin = ReflectionPlugin(self)
        self.__arrPlugins.append(self.__objReflectionPlugin)
        if not len(set(arrPlugins)) == len(arrPlugins):
            raise JSONRPCException(
                "The client filter plugin list contains duplicates.", JSONRPCException.INVALID_PARAMS
            )
        self.__arrPlugins = list(arrPlugins)

        logging.basicConfig(filename=dictParams["strLogFilePath"], format="%(asctime)s %(message)s")
        self.__objLogger = logging.getLogger(__name__)

    def getMethodMapper(self):
        """
        Method mapper getter method.
        """
        return self.__objMethodMapper

    def processRequest(self, strJSONRequest=None):
        """
        Processes the request and returns the response. In case of notifications no
        output is provided.

        @param string strJSONRequest

        @return string strResponse
        """
        bNotificationMode = False
        dictResponse = {
            "jsonrpc": self.__JSONRPC_VERSION,
            "id": None
        }

        try:
            bNotificationMode, dictRequest = self.__processResponse(strJSONRequest)
            self._verifyAcces()
            dictResponse = self._createResponse(dictRequest)
        except Exception as exc:
            self._logException(exc)

            if "result" in dictResponse:
                del dictResponse["result"]

            dictResponse["error"] = self._formatException(exc)
        finally:
            try:
                strResponse = json.dumps(dictResponse)
                for objPlugin in self.__arrPlugins:
                    objPlugin.sendResponse(strResponse)
            except Exception as exc:
                if not "error" in dictResponse:
                    if "result" in dictResponse:
                        del dictResponse["result"]

                    dictResponse["error"] = self._formatException(exc)
                    strResponse = json.dumps(dictResponse)

        if bNotificationMode:
            return None

        return strResponse

    def __processResponse(self, strJSONRequest):
        """
        @param string strJSONRequest

        @return array bNotificationMode, dictRequest
        """

        bNotificationMode = False

        """
        If there is no request, then that must mean that we are sending request by console.
        """
        if (strJSONRequest == None):
            strJSONRequest = input()
            self.bAuthenticated = True
            self.bAuthorized = True

        for objPlugin in self.__arrPlugins:
            strJSONRequest = objPlugin.beforeJSONDecode(strJSONRequest)

        if not isinstance(strJSONRequest, string_types):
            raise JSONRPCException(
                "The request must be a string.", JSONRPCException.PARSE_ERROR
            )

        strJSONRequest = strJSONRequest.strip()
        if len(strJSONRequest) == 0:
            raise JSONRPCException(
                "The request string cannot be empty.", JSONRPCException.PARSE_ERROR
            )

        try:
            dictRequest = json.loads(strJSONRequest, object_hook=self._decode_dict)
        except Exception:
            raise JSONRPCException(
                "The request must be a valid JSON encoded string.", JSONRPCException.PARSE_ERROR
            )

        bNotificationMode = self._checkRequest(dictRequest)
        if not "params" in dictRequest:
            dictRequest["params"] = []

        for objPlugin in self.__arrPlugins:
            dictRequest = objPlugin.afterJSONDecode(dictRequest)

        return bNotificationMode, dictRequest

    def _verifyAcces(self):
        """
        """
        if not self.bAuthenticated:
            raise JSONRPCException(
                "Not authenticated (bad credentials or signature).",
                JSONRPCException.NOT_AUTHENTICATED
            )

        if not self.bAuthorized:
            raise JSONRPCException(
                "Authenticated user is not authorized.",
                JSONRPCException.NOT_AUTHORIZED
            )

    def _createResponse(self, dictRequest):
        """
        @param object dictResponse
        @param object dictRequest

        @return object dictResponse
        """
        dictResponse = {
            "jsonrpc": self.__JSONRPC_VERSION,
            "id": dictRequest["id"]
        }

        try:
            dictResponse["result"] = self._callFunction(
                dictRequest["method"], dictRequest["params"]
            )
        except Exception as exc:
            for objPlugin in self.__arrPlugins:
                objPlugin.onException(exc)
            raise

        return dictResponse

    def _checkRequest(self, dictRequest):
        """
        Validates the request. Returns True or False if the request is a notification or not.

        @param object dictRequest

        @return boolean bNotificationMode
        """
        if isinstance(dictRequest, list):
            raise JSONRPCException(
                "JSON-RPC batch requests are not supported by this server",
                JSONRPCException.INVALID_REQUEST
            )
        elif not isinstance(dictRequest, dict):
            raise JSONRPCException(
                "The request must be an encoded associative array.",
                JSONRPCException.INVALID_REQUEST
            )

        if not "jsonrpc" in dictRequest or dictRequest["jsonrpc"] != self.__JSONRPC_VERSION:
            raise JSONRPCException(
                "The \"jsonrpc\" version must be equal to " + self.__JSONRPC_VERSION + ".",
                JSONRPCException.INVALID_REQUEST
            )

        bNotificationMode = not "id" in dictRequest
        if not bNotificationMode and not isinstance(dictRequest["id"], int):
            raise JSONRPCException(
                "The \"id\" key must be an integer.", JSONRPCException.INVALID_REQUEST
            )

        if not "method" in dictRequest or not isinstance(dictRequest["method"], string_types):
            raise JSONRPCException(
                "The \"method\" key must be a string.", JSONRPCException.INVALID_REQUEST
            )

        if "params" in dictRequest and not isinstance(dictRequest["params"], list):
            raise JSONRPCException(
                "The \"params\" key must be an array.", JSONRPCException.INVALID_REQUEST
            )

        return bNotificationMode

    def _callFunction(self, strFunctionName, arrParams):
        """
        Calls the function with the given parameters. If type checking is enabled, the types of
        the parameters and of the returned object are checked against the function reflection.

        @param string strFunctionName
        @param array arrParams

        @return mixed mxResult
        """
        for objPlugin in self.__arrPlugins:
            strFunctionName = objPlugin.resolveFunction(strFunctionName)

        """ Type checking is not done for functions that are called by the plugins. The plugins
        should implement its own type checking. """
        bCalled = False
        for objPlugin in self.__arrPlugins:
            bCalled, mxResult = objPlugin.callFunction(strFunctionName, arrParams)
            if bCalled:
                break

        if not bCalled:
            fnCallable = self.__objMethodMapper.map(strFunctionName)
            if fnCallable is None:
                raise JSONRPCException(
                    "The function \"" + strFunctionName + "\" does not exist or is not exported.",
                    JSONRPCException.METHOD_NOT_FOUND
                )

            dictReflection = self.__objReflectionPlugin.getReflection(strFunctionName)
            self._checkParameters(dictReflection, arrParams)
            mxResult = fnCallable(*arrParams)
            self._checkReturnValue(dictReflection, mxResult)

        return mxResult

    def _checkParameters(self, dictReflection, arrParams):
        """
        Checks the parameters against the function reflection.

        @param object dictReflection
        @param array arrParams
        """
        if len(arrParams) > len(dictReflection["function_parameters"]):
            raise JSONRPCException(
                "The function \"%s\" expects %d parameter(s). %d parameter(s) given."
                % (
                    dictReflection["function_name"],
                    len(dictReflection["function_parameters"]),
                    len(arrParams)
                ),
                JSONRPCException.INVALID_PARAMS
            )

        if len(dictReflection["function_parameters"]) > len(arrParams):
            if not "parameter_default_value_json" in dictReflection["function_parameters"][len(arrParams)]:
                raise JSONRPCException(
                    "The parameter with index %d of the \"%s\" function does not have a default value."
                    % (
                        len(arrParams),
                        dictReflection["function_name"]
                    ),
                    JSONRPCException.INVALID_PARAMS
                )

        for i in range(0, len(arrParams)):
            if not self._checkType(dictReflection["function_parameters"][i]["parameter_type"], arrParams[i]):
                raise JSONRPCException(
                    "The function \"%s\" expects the parameter with index %d to be a %s value."
                    % (
                        dictReflection["function_name"],
                        i,
                        dictReflection["function_parameters"][i]["parameter_type"]
                    ),
                    JSONRPCException.INVALID_PARAMS
                )

    def _checkReturnValue(self, dictReflection, mxReturnValue):
        """
        Checks the returned value against the function reflection.

        @param object dictReflection
        @param mixed mxReturnValue
        """
        if not self._checkType(dictReflection["function_return_type"], mxReturnValue):
            raise JSONRPCException(
                "The value returned by the \"%s\" function is inconsistent with the defined return type."
                % (dictReflection["function_name"]),
                JSONRPCException.INVALID_RETURN_TYPE
            )
        pass

    def _checkType(self, strType, mxVal):
        """
        Checks the type of a value.

        @param string strType
        @param mixed mxVal

        @return True or False
        """
        dictTypes = {
            "integer": int,
            "float": float,
            "string": string_types,
            "array": list,
            "boolean": bool,
            "object": dict,
            "mixed": object,
            "unknown": object
        }

        if strType == "None":
            return mxVal is None

        assert strType in dictTypes, "Parameter type \"%s\" not supported." % strType

        return isinstance(mxVal, dictTypes[strType])

    def _formatException(self, exc, bIncludeStackTrace=True):
        """
        Formats an exception as an associative array with message and code keys properly set.

        @param exception exc
        @param boolean bIncludeStackTrace

        @return a object
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

    def _logException(self, exc):
        """
        @param exception exc
        """

        """
        Logs an exception.
        """
        dictExc = self._formatException(exc, False)
        self.__objLogger.exception(dictExc["message"])

    def _decode_dict(self, data):
        """
        @param data

        @return a decoded object
        """
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = self._decode_list(value)
            elif isinstance(value, dict):
                value = self._decode_dict(value)
            rv[key] = value
        return rv

    def _decode_list(self, data):
        """
        @param data

        @return a decoded list
        """
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self._decode_list(item)
            elif isinstance(item, dict):
                item = self._decode_dict(item)
            rv.append(item)
        return rv
