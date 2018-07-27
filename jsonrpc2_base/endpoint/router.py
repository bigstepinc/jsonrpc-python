from __future__ import print_function
import json
import os
from sys import exit


class Router(object):
    """
    """

    _dictURLPathToClassName = None

    """
    * @param array arrURLPathToClassName. Associative array. URLs as keys.
    *    Class names should be fully qualified with namespace.
    *    URLs must be absolute, yet must not start or end with a slash.
    * @param string strRequestURI. Should be read from os.environ["REQUEST_URI"].
    * @return None.
    """

    def __init__(self, dictURLPathToClassName, strRequestURI):
        """Not validating class names to not invoke the autoloader, if any. """
        self._dictURLPathToClassName = dictURLPathToClassName

        self._route(strRequestURI)

    """
    * @param string strRequestURI. Should be os.environ["REQUEST_URI"].
    * @return null.
    """

    def _route(self, strRequestURI):
        if not isinstance(strRequestURI, basestring):
            raise Exception("strRequestURI must be a string.")

        """WARNING: Remove slash error-prone. May not behave as expected"""
        strRequestURI.strip("/")

        """WARNING: Check 2"""
        arrURLParts = strRequestURI.split("/", 2)

        """clean GET params from source URL aka get what's before the ?"""
        strRequestURI = strRequestURI.split("?", 2)[0]

        """clean trailing slash"""
        strRequestURI.rstrip("/")

        if strRequestURI in self._dictURLPathToClassName:
            endpoint = self._dictURLPathToClassName[strRequestURI]()
        elif strRequestURI + "/" in self._dictURLPathToClassName:
            endpoint = self._dictURLPathToClassName[strRequestURI + "/"]()
        else:
            if "REQUEST_METHOD" in os.environ and os.environ.get("REQUEST_METHOD") == "GET":
                """
                header("Content-type: text/html")
                """

                print("Page not found. Unknown JSON-RPC endpoint URL: " + strRequestURI)
            else:
                """
                header("HTTP/1.1 404 Not Found", true, 404)
                //header("Content-Type: text/plain charset=utf-8")
                header("Content-type: application/json")

                header("Cache-Control: no-cache, must-revalidate")
                header("Expires: Mon, 26 Jul 1991 05:00:00 GMT")
                header("Accept-Ranges: none")
                header("Connection: close")
                """

                print(json.loads(
                    '"jsonrpc": "2.0", "error": {"code": -32099, "message":' + os.environ.get("HTTP_HOST") + \
                    '...Unknown JSON-RPC endpoint URL: ' + strRequestURI + '), "id": None'))

            exit(1)
