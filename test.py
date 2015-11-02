from JSONRPCBaseException import JSONRPCBaseException;


class TestException(JSONRPCBaseException):
    RANDOM_ERROR = 42;



def test1(strString, bCalled = True, nTimes = 2):
    """
    Functie de test 1.

    @param String strString Bla bla.
    @param boolean bCalled = True Cra cra.
    @param int A = 2 aha aha

    @return None
    """
    return 4;

def test2():
    return 0;

def test3():
    return "test";
