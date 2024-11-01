"""
Module for JSON-RPC utility functions.
"""

error_list = {
    'Parse error': -32700, 'Invalid Request': -32600, 'Method not found': -32601,
    'Invalid params': -32602, 'Internal error': -32603, 'Unknown error': -32000,
    'Divided by zero': -32001}


def request(rcp_method, rcp_params, rcp_id=None):
    """
    Constructs a JSON-RPC request message.

    Args:
        rcp_method (str): The name of the method to be invoked.
        rcp_params (list): A list of parameters to be passed to the method.
        rcp_id (int, optional): An identifier for the request. Defaults to None.

    Returns:
        dict: The constructed JSON-RPC request message.
    """
    for index, param in enumerate(rcp_params):
        if isinstance(param, str) and param.isnumeric():
            rcp_params[index] = int(param)

    message = {'jsonrpc': '2.0', 'method': rcp_method.lower(), 'params': rcp_params}
    if rcp_id is not None:
        message['id'] = rcp_id

    return message


def result(rcp_result, rcp_id=None):
    """
    Constructs a JSON-RPC response message with a result.

    Args:
        rcp_result (any): The result to be included in the response.
        rcp_id (int, optional): An identifier for the response. Defaults to None.

    Returns:
        dict: The constructed JSON-RPC response message.
    """
    message = {'jsonrpc': '2.0', 'result': rcp_result}
    if rcp_id is not None:
        message['id'] = rcp_id

    return message


def error(rcp_error, rcp_id=None):
    """
    Constructs a JSON-RPC response message with an error.

    Args:
        rcp_error (str): The error message to be included in the response.
        rcp_id (int, optional): An identifier for the response. Defaults to None.

    Returns:
        dict: The constructed JSON-RPC response message with an error.
    """
    rcp_error_message = str(rcp_error)
    rcp_error_code = error_list.get(rcp_error_message, -32000)
    message = {
        'jsonrpc': '2.0', 'error': {'code': rcp_error_code, 'message': rcp_error_message}}
    if rcp_id is not None:
        message['id'] = rcp_id

    return message
