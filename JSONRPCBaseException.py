from traceback import format_exc


class JSONRPCBaseException(Exception):
    """
    JSONRPC Base Exception class. Should be extended by all applications that use JSONRPC.
    """

    """
    Exception code.
    """
    __nCode = None

    def __init__(self, strMessage, nCode):
        """
        Class constructor. Initializes the exception message and code.
        """
        super(JSONRPCBaseException, self).__init__(strMessage)

        self.__nCode = nCode

    def getMessage(self):
        """
        Getter method for the exception message.

        @return a message
        """
        return str(self)

    def getCode(self):
        """
        Getter method for the exception code.

        @return a code
        """
        return self.__nCode

    def getStackTrace(self):
        """
        Getter method for the exception stack trace.

        @return the exception StrackTrace
        """
        return format_exc()
