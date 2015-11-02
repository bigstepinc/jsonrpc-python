import inspect;


class MethodMapper(object):
    """
    * Maps method names to methods. Works on class instances and modules.
    """

    """
    * Method mappings.
    """
    __dictMethods = {};


    def __init__(self, dictObjectsToMethods):
        """
        * Class constructor.
        """
        for obj in dictObjectsToMethods:
            arrMethods = dict(inspect.getmembers(obj, inspect.isroutine));
            for strMethod in arrMethods:
                assert strMethod in arrMethods, "Method %s not found in object." % strMethodName
                self.__dictMethods[strMethod] = arrMethods[strMethod];

    def map(self, strMethodName):
        """
        * Maps a method name to a method and returns it.
        """
        if strMethodName in self.__dictMethods:
            return self.__dictMethods[strMethodName];

        return None;

    def getMethods(self):
        """
        * Retuns a list of all mapped methods.
        """
        return self.__dictMethods.keys();
