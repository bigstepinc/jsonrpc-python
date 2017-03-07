class ClientPluginBase(object):
    """
    JSON-RPC 2.0 client plugin base class.
    This is the class every other client filter plugin class should extend.
    """

    def __init__(self):
        """
        Class constructor.
        """
        pass

    def beforeJSONEncode(self, dictRequest):
        """
        Should be used to:
        - add extra request object keys
        - translate or encode output params into the expected server request object format.

        @param object dictRequest

        @return object dictRequest
        """
        return dictRequest

    def afterJSONEncode(self, strJSONRequest, strEndPointURL, dictHTTPHeaders):
        """
        Should be uset to:
        - encrypt, encode or otherwise prepare the JSON request string into the expected server input format
        - log raw input.

        @param string strJSONRequest
        @param string strEndPointURL
        @param object dictHTTPHeaders

        @return array strJSONRequest, strEndPointURL, dictHTTPHeaders
        """
        return strJSONRequest, strEndPointURL, dictHTTPHeaders

    def makeRequest(self, bCalled, strJSONRequest, strEndPointURL):
        """
        First plugin to make request will be the last one. The respective plugin MUST set bCalled to true.

        @param boolean bCalled
        @param string strJSONRequest
        @param string strEndPointURL

        @return array bCalled, strJSONRequest, strEndPointURL
        """
        return bCalled, strJSONRequest, strEndPointURL

    def beforeJSONDecode(self, strJSONResponse):
        """
        Should be used to:
        - decrypt, decode or otherwise prepare the JSON response into the expected JSON-RPC client format
        - log raw input.

        @param string strJSONResponse

        @return string strJSONResponse
        """
        return strJSONResponse

    def afterJSONDecode(self, strResult, mxResponse):
        """
        Should be used to:
        - add extra response object keys
        - translate or decode response params into the expected JSON-RPC client response object format.

        @param string strResult
        @param mixed mxResponse

        @return array strResult, mxResponse
        """
        return strResult, mxResponse

    def exceptionCatch(self, exception):
        """
        Should be used to rethrow exceptions as different types.
        The first plugin to throw an exception will be the last one.
        If there are no filter plugins registered or none of the plugins have throw exception,
        then client will throw the original JSONRPCException.

        @param error exception

        @return error exception
        """
        return exception
