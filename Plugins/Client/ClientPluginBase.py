class ClientPluginBase(object):
    """
    JSON-RPC 2.0 client plugin base class.
    This is the class every other client filter plugin class should extend.
    """

    def __init__(self):
        """
        Class constructor.
        """
        pass;

    def beforeJSONEncode(self, dictFilterParams):
        """
        Should be used to:
        - add extra request object keys;
        - translate or encode output params into the expected server request object format.

        @param dictionary dictFilterParams. It is used for reference return for multiple variables,
        which can be retrieved using specific keys
        - "dictRequest"

        @return dictionary dictFilterParams
        """
        return dictFilterParams;

    def afterJSONEncode(self, dictFilterParams):
        """
        Should be uset to:
        - encrypt, encode or otherwise prepare the JSON request string into the expected server input format;
        - log raw input.

        @param dictionary dictFilterParams. It is used for reference return for multiple variables,
        which can be retrieved using specific keys
        - "strJSONRequest"
        - "strEndPointURL"
        - "dictHTTPHeaders"

        @return dictionary dictFilterParams
        """
        return dictFilterParams;

    def makeRequest(self, dictFilterParams):
        """
        First plugin to make request will be the last one. The respective plugin MUST set bCalled to true.

        @param dictionary dictFilterParams. It is used for reference return for multiple variables,
        which can be retrieved using specific keys
        - "mixed". The RAW string output of the server or false on error (or can throw)

        @return dictionary dictFilterParams
        """
        return dictFilterParams;

    def beforeJSONDecode(self, dictFilterParams):
        """
        Should be used to:
        - decrypt, decode or otherwise prepare the JSON response into the expected JSON-RPC client format;
        - log raw input.

        @param dictionary dictFilterParams. It is used for reference return for multiple variables,
        which can be retrieved using specific keys
        - "strJSONResponse"

        @return dictionary dictFilterParams
        """
        return dictFilterParams;

    def afterJSONDecode(self, dictFilterParams):
        """
        Should be used to:
        - add extra response object keys;
        - translate or decode response params into the expected JSON-RPC client response object format.

        @param dictionary dictFilterParams. It is used for reference return for multiple variables,
        which can be retrieved using specific keys
        - "dictResponse"

        @return dictionary dictFilterParams
        """
        return dictFilterParams;

    def exceptionCatch(self, exception):
        """
        Should be used to rethrow exceptions as different types.
        The first plugin to throw an exception will be the last one.
        If there are no filter plugins registered or none of the plugins have throw exception,
        then Client will throw the original JSONRPCException.

        @param Error exception

        @return Error exception
        """
        return exception;
