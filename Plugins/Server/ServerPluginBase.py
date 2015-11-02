from abc import ABCMeta, abstractmethod;


class ServerPluginBase(object):
    """
    * Server plugin base class. Methods are not declared abstract because the plugins should not
    * be forced to reimplement all of them.
    """

    """
    * The server plugin base must be abstract. It should not be instantiated.
    """
    __metaclass__ = ABCMeta;

    """
    * The server instance is useful for most plugins.
    """
    _objServer = None;


    def __init__(self):
        """
        * Class constructor.
        """
        pass;

    def beforeJSONDecode(self, strJSONRequest):
        """
        * Method that is called before the request is deserialized. A plugin may modify the request
        * and return the updated request.
        """
        return strJSONRequest;

    def afterJSONDecode(self, dictRequest):
        """
        * Method that is called after the request is deserialized. A plugin may modify the request
        * and return the updated request.
        """
        return dictRequest;

    def resolveFunction(self, strFunctionName):
        """
        * Method that is called to resolve a function name. A plugin may resolve a function and
        * return the resolved name.
        """
        return strFunctionName;

    def callFunction(self, strFunctionName, arrParams):
        """
        * Method that is called to execute the function. A plugin that calls the function must
        * the tuple (bCalled, mxResult) with bCalled set.
        """
        return (False, None);

    def onException(self, exc):
        """
        * Method that is called on exceptions.
        """
        pass;

    def sendResponse(self, dictResponse):
        """
        * Method that is called to on server response.
        """
        pass;

    def setServerInstance(self, objServer):
        """
        * Server instance setter method.
        """
        self._objServer = objServer;
