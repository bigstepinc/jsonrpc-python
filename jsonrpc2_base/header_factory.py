import base64

class HeaderFactory(object):
    """
    """

    def create(self, strUser, strPassword, strContentType):
        """
        @param string strUser
        @param string strPassword
        @param string strContentType

        @return object
        """
        dictHTTPHeaders = {
            "Content-Type": strContentType
        }

        if strUser is not None and strPassword is not None:
            dictHTTPHeaders["Authorization"] = "Basic " + base64.b64encode(strUser + ":" + strPassword)

        return dictHTTPHeaders
