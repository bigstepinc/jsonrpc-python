from abc import ABCMeta


class ServerPluginBase(object):
    """
    server plugin base class. Methods are not declared abstract because the plugins should not
    be forced to reimplement all of them.
    """

    """
    The server plugin base must be abstract. It should not be instantiated.
    """
    __metaclass__ = ABCMeta

    """
    The server instance is useful for most plugins.
    """
    _objServer = None

    def __init__(self):
        """
        Class constructor.
        """
        pass

    def beforeJSONDecode(self, strJSONRequest):
        """
        Method that is called before the request is deserialized. A plugin may modify the request
        and return the updated request.

        @param string strJSONRequest

        @return string strJSONRequest
        """
        return strJSONRequest

    def afterJSONDecode(self, dictRequest):
        """
        Method that is called after the request is deserialized. A plugin may modify the request
        and return the updated request.

        @param object dictRequest

        @return object dictRequest
        """
        return dictRequest

    def resolveFunction(self, strFunctionName):
        """
        Method that is called to resolve a function name. A plugin may resolve a function and
        return the resolved name.

        @param string strFunctionName

        @return string strFunctionName
        """
        return strFunctionName

    def callFunction(self, strFunctionName, arrParams):
        """
        Method that is called to execute the function. A plugin that calls the function must
        the tuple (bCalled, mxResult) with bCalled set.

        @param string strFunctionName

        @return array arrParams
        """
        return (False, None)

    def onException(self, exc):
        """
        Method that is called on exceptions.

        @param exception exc
        """
        pass

    def sendResponse(self, dictResponse):
        """
        Method that is called to on server response.

        @param object dictResponse
        """
        pass

    def setServerInstance(self, objServer):
        """
        server instance setter method.

        @param object objServer
        """
        self._objServer = objServer
