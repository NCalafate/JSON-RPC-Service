"""
 Simple JSON-RPC Server

"""

import json
import socket

import functions
import jsonrpc


class JSONRPCServer:
    """The JSON-RPC server."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.funcs = {}

    def register(self, name, function):
        """Registers a function."""
        self.funcs[name] = function

    def start(self):
        """Starts the server."""
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f'»»» Listening on port {self.port} ...')

        try:
            while True:
                # Accepts and handles client
                conn, _ = self.sock.accept()
                self.handle_client(conn)

                # Close client connection
                conn.close()

        except ConnectionAbortedError:
            pass
        except OSError:
            pass

    def stop(self):
        """Stops the server."""
        self.sock.close()

    def handle_client(self, conn):
        """
        Executes the requested function and sends the response.

        Parameters:
            conn (socket or any): The client socket connection.

        Raises:
            ValueError: If there's an error executing the function.

        Returns:
            tuple: A tuple containing the original message and the response message.
        """

        # Receive Message
        msg = conn.recv(1024).decode()

        if not msg:
            return None, None

        print(f'--> {msg}')

        try:

            # Validate Objects
            try:
                msg = json.loads(msg)
            except ValueError as e:
                raise ValueError('Parse error') from e
            except Exception as e:
                raise ValueError('Unknown Error') from e

            if (not isinstance(msg, dict) or 'jsonrpc' not in msg or msg[
                 'jsonrpc'] != '2.0' or 'method' not in msg or msg['method'] is None):
                raise ValueError('Invalid Request')

            if 'id' not in msg or msg['id'] is None:
                return msg, None

            # Read Objects
            msg_method = msg.get('method').lower()
            msg_params = msg.get('params', [])
            msg_id = msg.get('id')

            # Execute Function
            if msg_method not in self.funcs:
                raise ValueError('Method not found')

            func = self.funcs[msg_method]

            try:
                result = func(*msg_params)
            except TypeError as e:
                raise ValueError('Invalid params') from e
            except ZeroDivisionError as e:
                raise ValueError('Divided by zero') from e
            except Exception as e:
                raise ValueError('Unknown Error') from e

            # Send Response
            msg_response = jsonrpc.result(result, msg_id)
            print(f'<-- {msg_response}')

            conn.sendall(json.dumps(msg_response).encode())
            return msg, msg_response

        except ValueError as e:

            # Read Objects
            msg_id = None\
                if (not isinstance(msg, dict) or 'id' not in msg or msg['id'] is None)\
                else msg['id']

            # Send Response
            msg_response = jsonrpc.error(e, msg_id)
            conn.sendall(json.dumps(msg_response).encode())
            print(f'<-- {msg_response}')
            return msg, msg_response


if __name__ == "__main__":
    # Test the JSONRPCServer class
    server = JSONRPCServer('0.0.0.0', 8000)

    # Register functions
    server.register('hello', functions.hello)
    server.register('greet', functions.greet)
    server.register('add', functions.add)
    server.register('sub', functions.sub)
    server.register('mul', functions.mul)
    server.register('div', functions.div)

    # Start the server
    server.start()
