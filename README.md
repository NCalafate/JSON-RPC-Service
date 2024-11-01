> IPS - Escola Superior de Tecnologia de Setúbal
> 
> LEI - Computação Paralela e Distribuída 2023 / 2024



# Practical Assignment #2 – JSON-RPC Service

## Solution

### Client

#### client.py / invoke
This function was modified to send requests in the JSON-RPC format, including the function arguments (method and params) and the ID, which is incremented with each request. The response message is then validated by the function 'jrpc_parse', raising an exception if it is invalid.

#### client.py / jrpc_parse
This function validates a response message, performing the following checks:
- ID: Messages without an ID are generally ignored and return None. However, to allow for use in extras, the function returns the message to receive system or broadcast messages.
- Result: If the message contains a result, it is returned.
- Error: If the message is an error message, an exception is raised.

### Server

#### server.py / handle_client
It was adjusted to receive and send requests in the JSON-RPC format. It returns a tuple representing the received message and the response message, enabling this function's use in extras.

Validations are performed to respond according to the received request:
- ID: If the message does not contain an ID, no response is sent.
- Result: If the message and request are valid, a response with the result is sent.
- Error: If the message or request is invalid, a response message with the error information is sent.

### Global
#### jsonrpc.py - Centralization of Errors and JSON-RPC
The Python file 'jsonrpc.py' was created to centralize all known errors, making them easier to look up and edit. This file contains three functions that return a dictionary in JSON-RPC 2.0 format.

### Pylint
Pylint was used to analyze and correct any errors, resulting in the following scores:

- cliente.py: 9.59
- server.py: 10
- jsonrpc.py: 10


## Extras
### Backward Compatibility
To ensure that 'client.py' and 'server.py' pass the original tests, the extras were developed in additional files that extend them, maintaining backward compatibility. This means the original version can communicate with an extended version.

### Reuse of TCP/IP Connections
The connection between the client and server is continuous and is only closed when one of the programs is terminated or when the server receives a request for logout, kick, or shutdown.

### Parallel Clients
For each connected client, the server starts a dedicated thread to respond to requests, allowing it to handle multiple clients simultaneously.

### Asynchronous Responses
Upon connecting to the server, the client starts a thread to receive messages continuously.

### Client input
Converts a user’s written input into a JSON-RPC formatted request and sends it.

Example usage:
> hello
> 
> greet Ricardo
> 
> add3 1 3 5
 
### Commandos SUDO
The concept of notifications was used to implement the idea of 'SUDO' requests, which cause the server to take action. The following commands were developed:

- help: The server returns a message with all registered functions.
- broadcast: Sends a message to all connected clients.
- exit: Ends the connection with the client.
- kick: Ends connections with all other connected clients.
- shutdown: Ends connections with all clients and shuts down the server.

Example usage:
> sudo help
> 
> sudo kick
> 
> sudo broadcast Isto é uma mensagem de broadcast
