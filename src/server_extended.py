"""
 Simple JSON-RPC Server Extended.

"""

import inspect
import json
import os
import signal
import socket
import threading

import functions
from server import JSONRPCServer


class ExtendedJSONRPCServer(JSONRPCServer):
    """The JSON-RPC server extended."""

    def __init__(self, host, port):
        super().__init__(host, port)
        self.connection_list = []

    def register_all(self, module):
        """
        Registers all functions from a module.

        This method iterates through all attributes of the specified module.
        If an attribute is callable, it is registered with the server.

        Parameters:
            module (module): The module containing the functions to register.
        """
        for name in dir(module):
            func = getattr(module, name)
            if callable(func):
                self.register(name, func)

    def start(self):
        """
        Starts the Extended JSONRPC server.

        This method initializes the server socket, binds it to the specified
        host and port, and starts listening for incoming connections. Once a
        connection is established, it creates a new thread to handle the client
        connection.
        """
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print('»»» Extended JSONRPC Server initialized')
        print(f'»»» Listening on port {self.port} ...')

        while True:
            conn, _ = self.sock.accept()
            print('»»» User connected')
            self.connection_list += [conn]
            threading.Thread(target=self.client_thread, args=[conn]).start()

    def handle_notify(self, conn, msg):
        """
        Handles notifications received from a client connection.

        Parameters:
            conn (socket): The client socket connection.
            msg (dict): The message received from the client.

        Returns:
            dict or None: The modified message if handled successfully, None otherwise.
        """
        if not msg or 'id' in msg and msg['id'] is not None:
            return None

        method = msg['method']
        params = None if 'params' not in msg else msg['params']

        if params is not None:
            if method == 'broadcast':
                self.notify_broadcast(params)

        if method == 'help':
            self.notify_help(conn)
        if method == 'kick':
            self.notify_kick(conn)
        if method in ('exit', 'quit', 'logout', 'logoff'):
            self.notify_exit(conn)
        if method == 'shutdown':
            self.notify_shutdown()
            return True

        return msg

    def notify_help(self, conn):
        """
        Sends a list of all registered functions to the client.

        Parameters:
            conn (socket or any): The client socket connection.
        """
        registered_funcs = {}
        for name, func in self.funcs.items():
            registered_funcs[name] = str(inspect.signature(func))
        message = {"message": {"functions": registered_funcs}}
        print(f'«-- {message}')
        conn.sendall(json.dumps(message).encode())

        message = {"message": {"sudo": ["help", "broadcast", "exit", "kick", "shutdown"]}}
        print(f'«-- {message}')
        conn.sendall(json.dumps(message).encode())



    def notify_broadcast(self, msg):
        """
        Sends a broadcast message to all client connections.

        Parameters:
            msg (list): A list of message strings to be broadcasted.
        """
        if len(msg) > 0:
            message = {'message': ' '.join(msg)}
            for conn in self.connection_list:
                conn.sendall(json.dumps(message).encode())
            print(f'«-- {message}')

    @staticmethod
    def notify_exit(conn):
        """
        Disconnects the client connection.

        Parameters:
            conn (socket): The client socket connection.
        """
        message = {"message": "Disconnecting client..."}
        print(f'«-- {message}')
        conn.sendall(json.dumps(message).encode())
        conn.close()

    def notify_kick(self, conn):
        """
        Disconnects all other client connections

        Parameters:
            conn (socket): The client socket connection to not disconnect.
        """
        for _ in self.connection_list:
            if _ != conn:
                self.notify_exit(_)

    def notify_shutdown(self):
        """
        Disconnects all clients and shuts down the server.
        """
        self.notify_broadcast(['Server shutting down ...'])
        for conn in self.connection_list:
            conn.close()
        self.connection_list.clear()
        os.kill(os.getpid(), signal.SIGTERM)

    def client_thread(self, conn):
        """
        Thread that handles client connections.

        This method continuously listens for messages from the client connection 'conn'.
        It accepts and handles each message received, while also handling notifications.
        If the received message is None, indicating the client has disconnected, the loop breaks.

        Parameters:
            conn (socket or any): The client socket connection.
        """
        try:
            while True:
                try:
                    # Accepts and handles client
                    msg, _ = self.handle_client(conn)
                    # Handle Notification
                    self.handle_notify(conn, msg)

                    if msg is None:
                        break

                except TypeError as e:
                    print(e)
                    pass

        except (ConnectionResetError, ConnectionAbortedError, OSError):
            pass
        finally:
            print('»»» User disconected')
            conn.close()
            self.connection_list.remove(conn)


# Example usage
if __name__ == "__main__":
    connection_list = []
    server = ExtendedJSONRPCServer('0.0.0.0', 8000)

    # Registar functions from module
    server.register_all(functions)

    # Start the server
    server.start()
