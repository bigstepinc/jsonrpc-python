import sys

class Serializer(object):
    @staticmethod
    def __encode(objOb, objClass):
        """
        @param object objOb
        @param object objClass

        @return object dictJSON. The dictionary from class.
        """
        dictJSON = {}

        arrAttr = dir(objOb)
        for strAttr in arrAttr:
            if not strAttr.startswith("__"):
                dictJSON[strAttr] = getattr(objOb, strAttr)

        return dictJSON

    @staticmethod
    def __recursive_encode(objOb):
        """
        @param object objOb

        @return a dictionary
        """
        if type(objOb).__name__ in Serializer.__arrPrimitiveTypes:
            return objOb

        if isinstance(objOb, list):
            for index in range(len(objOb)):
                objOb[index] = Serializer.__recursive_encode(objOb[index])

            return objOb
        elif isinstance(objOb, dict):
            for strKey in objOb:
                objOb[strKey] = Serializer.__recursive_encode(objOb[strKey])

            return objOb

        arrAttr = dir(objOb)
        for strAttr in arrAttr:
            if not strAttr.startswith("__"):
                setattr(objOb, strAttr, Serializer.__recursive_encode(getattr(objOb, strAttr)))

        return Serializer.__encode(objOb, getattr(sys.modules[__name__], type(objOb).__name__))

    @staticmethod
    def serialize(objOb):
        """
        @param object objOb

        @return object __dictDictionary. The dictionary from class.
        """
        if isinstance(objOb, dict):
            return objOb

        return Serializer.__recursive_encode(objOb)

    __arrPrimitiveTypes = [
        "int",
        "bool",
        "str",
        "unicode",
        "float",
        "NoneType"
    ]
