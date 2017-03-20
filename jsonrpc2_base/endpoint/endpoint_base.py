from jsonrpc2_base.server import Server


class EndpointBase(object):
    """
    """

    """
    * @type JSONRPC\Server
    """
    _server = None

    def __init__(self):
        """
        """
        self._preInit()
        self._instantiateServer()
        self._postInit()
        self._allowedExceptionsAndCodes()
        self._allowedFunctionCalls()
        self._addAndConfigurePlugins()
        self._processRequest()

    """
    * Code which needs to run before instantiating the JSONRPC\Server.
    * Maybe strict security validations, environment setup, etc.
    """

    def _preInit(self):
        raise Exception("Must override")

    """
    * \JSONRPC\Server is instantiated by default.
    """

    def _instantiateServer(self):
        if (self._server == None):
            self._server = Server()

    """
    * Setup logging, CORS pre-processing, etc.
    """

    def _postInit(self):
        raise Exception("Must override")

    """
    """

    def _allowedExceptionsAndCodes(self):
        raise Exception("Must override")

    """
     * Should append to \JSONRPC\Server::arrAllowedFunctionCalls.
    """

    def _allowedFunctionCalls(self):
        raise Exception("Must override")

    """
    """

    def _addAndConfigurePlugins(self):
        raise Exception("Must override")

    """
    * Last phase.
    """

    def _processRequest(self):
        self._server.processRequest()
