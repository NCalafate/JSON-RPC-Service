"""
 Simple JSON-RPC Client Extended

"""
import json
import os
import signal
import threading

from client import JSONRPCClient
from src import jsonrpc


class ExtendedJSONRPCClient(JSONRPCClient):
    """The JSON-RPC client extended."""

    def send(self, msg):
        """Sends a message to the server."""
        self.sock.sendall(msg.encode())
        print(f'<-- {msg}')

    def invoke(self, method_name, parameters):
        """
        Invokes a remote function using JSON-RPC.

        Parameters:
            method_name (str): The name of the remote method to be invoked.
            parameters (list or dict or tuple): The parameters to be passed
        """
        self.id += 1
        msg = jsonrpc.request(method_name, parameters, self.id)
        self.send(json.dumps(msg))

    def notify(self, method_name, parameters):
        """
        Sends a JSON-RPC 2.0 notification message.

        Parameters:
            method_name (str): The name of the notification method to be invoked.
            parameters (list or dict): The parameters to be included in the notification.
        """
        notification = jsonrpc.request(method_name, parameters, None)
        self.send(json.dumps(notification))

    def listening_thread(self):
        """
         Thread that listens for incoming messages.

         This method runs in a loop, listening for incoming messages from the server.
         It handles various exceptions to ensure that the thread can terminate gracefully.

         The thread will break the loop and terminate if:
             - It encounters a socket error (OSError).
             - It receives specific messages.

         Upon termination, it prints a termination message and sends a
         SIGTERM signal to the process to terminate the client.
         """

        try:
            while True:
                try:
                    # Receive and decode the message from the socket
                    msg = self.sock.recv(1024).decode()

                    if not msg:
                        break

                    print(f'--> {msg}')

                    # Parse the received JSON-RPC response message
                    msg = self.jrpc_parse(msg)

                except OSError:
                    break
                except Exception:
                    continue

        except Exception:
            pass
        finally:
            print('»»» Terminating client ...')
            os.kill(os.getpid(), signal.SIGTERM)


if __name__ == "__main__":

    try:
        # Initialize ExtendedJSONRPCClient
        client = ExtendedJSONRPCClient('127.0.0.1', 8000)
        (thread := threading.Thread(target=client.listening_thread, args=[])).start()

        print("»»» Extended JSONRPC Client initialized")
        print("»»» Type 'sudo help' for more information\n")

        while threading.active_count() > 1:
            try:
                command = input().split()

                if command:
                    if command[0].lower() == 'sudo' and len(command) > 1:
                        # Process sudo commands
                        client.notify(command[1], command[2:])
                        continue

                    # Process regular commands
                    try:
                        client.invoke(command[0].lower(), command[1:])
                    except Exception as e:
                        print(f'Error - Exception/Invoke: {e}')

            except KeyboardInterrupt:
                break
            except (ConnectionRefusedError, ConnectionAbortedError):
                break

    except OSError:
        pass
    except Exception as e:
        print(f'Error - Exception/Main: {e}')
    finally:
        print('»»» Extended JSONRPC Client terminated')
