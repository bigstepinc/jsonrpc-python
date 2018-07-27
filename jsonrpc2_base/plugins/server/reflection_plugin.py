import inspect
import re
from os import linesep
from jsonrpc2_base.plugins.server.server_plugin_base import ServerPluginBase


class ReflectionPlugin(ServerPluginBase):
    """
    server reflection plugin.
    """

    """
    Reflection plugin exported functions.
    """
    __dictReflectionFunctions = {
        "rpc.functions": "getFunctions",
        "rpc.reflectionFunction": "getReflection",
        "rpc.reflectionFunctions": "getReflections"
    }

    """
    Reflection plugin type mnemonics.
    """
    dictTypeMnemonics = {
        "n": "integer",
        "f": "float",
        "str": "string",
        "arr": "array",
        "b": "boolean",
        "dict": "object",
        "mx": "mixed"
    }

    def __init__(self, objServer):
        """
        Class constructor.

        @param object objServer
        """
        self.setServerInstance(objServer)

    def afterJSONDecode(self, dictRequest):
        """
        @param object dictRequest

        @return object dictRequest
        """
        if dictRequest["method"] in self.__dictReflectionFunctions:
            self._objServer.bAuthenticated = True
            self._objServer.bAuthorized = True

        return dictRequest

    def callFunction(self, strFunctionName, arrParams):
        """
        Calls the rpc functions exported by the plugin.

        @param string strFunctionName
        @param array arrParams

        @return an array
        """
        bCalled = False
        mxResult = None

        if strFunctionName in self.__dictReflectionFunctions:
            mxResult = getattr(
                self, self.__dictReflectionFunctions[strFunctionName]
            )(*arrParams)
            bCalled = True

        return (bCalled, mxResult)

    def getFunctions(self):
        """
        @return the list of exported functions
        """
        return self._objServer.getMethodMapper().getMethods()

    def getReflection(self, strFunctionName):
        """
        @param strFunctionName

        @return the function reflection. The function name must be resolved prior to getting its
        reflection
        """
        fnCallable = self._objServer.getMethodMapper().map(strFunctionName)
        assert inspect.isroutine(fnCallable), "The mapped function is not a routine."

        arrParams = self.__getFunctionArgSpec(fnCallable)
        dictSpec = self.__getFunctionDocSpec(fnCallable)

        """ TODO: Check the function prototype agains its doc comment. """

        return {
            "function_name": strFunctionName,
            "function_return_type": dictSpec["function_return_type"],
            "function_documentation_comment": dictSpec["function_documentation_comment"],
            "function_parameters": arrParams
        }

    def getReflections(self):
        """
        @return the list of reflections of all the function exported on the server
        """
        arrReflections = []

        arrFunctions = self.getFunctions()
        for strFunction in arrFunctions:
            arrReflections.append(self.getReflection(strFunction))

        return arrReflections

    def __getFunctionArgSpec(self, fnCallable):
        """
        @param fnCallable

        @return argument specification of the funciton
        """
        arrParams = []

        ntArgSpec = inspect.getargspec(fnCallable)
        assert ntArgSpec.varargs is None, "Variable arguments list functions not supported."

        arrParamNames = ntArgSpec.args
        arrDefaultValues = list(ntArgSpec.defaults or ())

        for strParamName in reversed(arrParamNames):
            strParamType = "unknown"
            strTypePrefix = re.search("^[a-z]*", strParamName).group(0)
            if strTypePrefix in self.dictTypeMnemonics:
                strParamType = self.dictTypeMnemonics[strTypePrefix]

            dictParam = {
                "parameter_name": strParamName,
                "parameter_type": strParamType
            }

            if len(arrDefaultValues) > 0:
                dictParam["parameter_default_value_json"] = arrDefaultValues.pop()
                """ TODO: check the type of the default value against the type inferred from the mnemonic. """

            arrParams.insert(0, dictParam)

        return arrParams

    def __getFunctionDocSpec(self, fnCallable):
        """
        @param fnCallable

        @return the complete specification of the function from the docstring
        """
        arrParams = []
        strReturnType = "unknown"

        strDoc = inspect.getdoc(fnCallable) or inspect.getcomments(fnCallable)
        arrDocLines = []
        if not strDoc is None:
            arrDocLines = strDoc.split(linesep)

        for strDocLine in arrDocLines:
            strDocLine = strDocLine.strip()

            objMatch = re.match(
                "^\s*@param\s+(\w+)\s+(\w+)(?:\s*=\s*(None|True|False|(?:\-?\d+(?:\.\d+)?)|(?:\".*\")))?.*$",
                strDocLine)
            if objMatch:
                dictParam = {
                    "parameter_name": objMatch.group(2),
                    "parameter_type": objMatch.group(1)
                }

                mxDefaultValue = objMatch.group(3)
                if mxDefaultValue:
                    if mxDefaultValue == "None":
                        mxDefaultValue = None
                    elif mxDefaultValue in ["True", "False"]:
                        mxDefaultValue = mxDefaultValue == "True"
                    else:
                        try:
                            mxDefaultValue = int(mxDefaultValue)
                        except:
                            try:
                                mxDefaultValue = float(mxDefaultValue)
                            except:
                                pass

                    dictParam["parameter_default_value_json"] = mxDefaultValue

                arrParams.append(dictParam)

                continue

            objMatch = re.match("^\s*@return\s+(None|(?:\w+))(?:\s*.*)?$", strDocLine)
            if objMatch:
                strReturnType = objMatch.group(1)

        return {
            "function_parameters": arrParams,
            "function_return_type": strReturnType,
            "function_documentation_comment": strDoc
        }
