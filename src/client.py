"""
 Simple JSON-RPC Client

"""

import json
import socket
import jsonrpc


class JSONRPCClient:
    """The JSON-RPC client."""

    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.id = 0

    def close(self):
        """Closes the connection."""
        self.sock.close()

    def send(self, msg):
        """Sends a message to the server."""
        self.sock.sendall(msg.encode())
        return self.sock.recv(1024).decode()

    def invoke(self, method_name, parameters):
        """
        Invokes a remote function using JSON-RPC.

        Parameters:
            method_name (str): The name of the remote method to be invoked.
            parameters (list or dict or tuple): The parameters to be passed
            to the remote method.

        Returns:
            dict: The response message received from the remote method
            invocation.
        """
        # Prepare JSON-RPC request
        self.id += 1
        msg = jsonrpc.request(method_name.lower(), parameters, self.id)

        # Send the JSON-RPC request message and receive the response
        msg_received = self.send(json.dumps(msg))
        print(f'<-- {msg}')
        print(f'--> {msg_received}')

        # Parse the received JSON-RPC response message
        msg_received = self.jrpc_parse(msg_received)

        return msg_received.get('result', 'error')

    @staticmethod
    def jrpc_parse(message):
        """
        Parses a JSON-RPC message.

        Parameters:
            message (str): The JSON-RPC message to be parsed.

        Returns:
            dict or None: The parsed JSON-RPC message, or None if the input
            message is empty or invalid.

        Raises:
            AttributeError: If the error code is -32601 (Method not found).
            TypeError: If the error code is -32602 (Invalid params).
            Exception: For other error codes present in the 'error' field.
        """
        if not message:
            return None

        msg = json.loads(message)

        if 'id' not in msg:
            return msg

        if 'result' in msg:
            return msg

        if 'error' in msg:
            error_code = msg['error'].get('code')
            error_message = msg['error']
            if error_code == -32601:
                raise AttributeError(error_message)
            if error_code == -32602:
                raise TypeError(error_message)
            raise Exception(error_message)

        return None

    def __getattr__(self, name):
        """Invokes a generic function."""

        def inner(*params):
            return self.invoke(name, params)

        return inner


if __name__ == "__main__":
    # Initialize JSONRPCClient
    client = JSONRPCClient('127.0.0.1', 8000)

    try:
        client.invoke('add', [3, 9])
    except Exception as e:
        pass
    finally:
        client.close()
