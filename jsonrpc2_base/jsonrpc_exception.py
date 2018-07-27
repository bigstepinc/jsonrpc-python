from jsonrpc2_base.jsonrpc_base_exception import JSONRPCBaseException


class JSONRPCException(JSONRPCBaseException):
    """
    JSONRPC Exception class.
    """

    """
    Bad credentials (user, password, signing hash, account does not exist, etc.). Not part of
    JSON-RPC 2.0 spec.
    """
    NOT_AUTHENTICATED = -1

    """
    The authenticated user is not authorized to make any or some requests. Not part of
    JSON-RPC 2.0 spec.
    """
    NOT_AUTHORIZED = -2

    """
    The request has expired. The requester must create or obtain a new request. Not part of
    JSON-RPC 2.0 spec.
    """
    REQUEST_EXPIRED = -3

    """
    Parse error. Invalid JSON was received by the server. An error occurred on the server while
    parsing the JSON text.
    """
    PARSE_ERROR = -32700

    """
    Invalid Request. The JSON sent is not a valid Request object.
    """
    INVALID_REQUEST = -32600

    """
    Method not found. The method does not exist or is not available.
    """
    METHOD_NOT_FOUND = -32601

    """
    Invalid params. Invalid method parameter(s).
    """
    INVALID_PARAMS = -32602

    """
    Internal error. Internal JSON-RPC error.
    """
    INTERNAL_ERROR = -32603

    """
    Invalid method return type.
    """
    INVALID_RETURN_TYPE = -32604
