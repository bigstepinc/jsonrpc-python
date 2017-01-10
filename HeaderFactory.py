import base64;

class HeaderFactory(object):
    def create(self, sUser, sPassword, sContentType):
        dictHTTPHeaders = {
            "Content-Type": sContentType
        }

        if sUser is not None and sPassword is not None:
            dictHTTPHeaders["Authorization"] = "Basic " + base64.b64encode(sUser + ":" + sPassword)

        return dictHTTPHeaders
