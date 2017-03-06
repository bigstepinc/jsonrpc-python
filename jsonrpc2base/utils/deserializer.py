import inspect
import json
import sys

class Deserializer(object):
    @staticmethod
    def __decode(dictJSON, objClass):
        """
        @param object dictJSON
        @param object objClass

        @return object objOb. The object from JSON.
        """
        arrInitParams = []
        try:
            # Get all parameters from constructor
            arrInitParams = inspect.getargspec(objClass.__init__)[0]
            # Delete the "self" element from array
            arrInitParams.pop(0)
        except Exception:
            # If objClass has no constructor then this catch will leave arrInitParams = [].
            pass

        # Vector used to initialize an object
        arrValueParams = []
        for strProperty in arrInitParams:
            arrValueParams.append(dictJSON[strProperty])

        objOb = objClass(*arrValueParams)

        arrAttr = dir(objOb)
        for strAttr in arrAttr:
            if (strAttr in arrInitParams) or (strAttr.startswith("__")):
                continue
            if strAttr in dictJSON.keys():
                setattr(objOb, strAttr, dictJSON[strAttr])
            else:
                setattr(objOb, strAttr, getattr(objOb, strAttr))

        return objOb

    @staticmethod
    def __recursive_decode(mxJSON):
        """
        @param mixed mxJSON

        @return mixed mxJSON. The object from JSON
        """
        if type(mxJSON).__name__ in Deserializer.__arrPrimitiveTypes:
            return mxJSON

        if isinstance(mxJSON, list):
            for index in range(len(mxJSON)):
                mxJSON[index] = Deserializer.__recursive_decode(mxJSON[index])

            return mxJSON
        elif isinstance(mxJSON, dict):
            for strKeyJSON in mxJSON:
                mxJSON[strKeyJSON] = Deserializer.__recursive_decode(mxJSON[strKeyJSON])

            if "type" in mxJSON:
                return Deserializer.__decode(mxJSON, getattr(sys.modules[__name__], mxJSON["type"]))

            return mxJSON

        arrAttr = dir(mxJSON)
        for strAttr in arrAttr:
            if not strAttr.startswith("__"):
                setattr(mxJSON, strAttr, Deserializer.__recursive_decode(getattr(mxJSON, strAttr)))

        return mxJSON

    @staticmethod
    def deserialize(mxJSON):
        """
        @param mixed mxJSON

        @return an object from JSON
        """
        if isinstance(mxJSON, basestring):
            dictJSON = json.loads(mxJSON)
        elif isinstance(mxJSON, dict):
            dictJSON = mxJSON
        else:
            raise Exception("Wrong input. Only strings or dictionaries are accepted.")

        return Deserializer.__recursive_decode(dictJSON)

    __arrPrimitiveTypes = [
        "int",
        "bool",
        "str",
        "unicode",
        "float",
        "NoneType"
    ]
