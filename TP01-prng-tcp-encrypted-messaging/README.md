# TP01 - PRNG and Encrypted TCP Messaging

This practical work implements a simple encrypted communication between two computers using Python.

The objective is to combine cryptographic concepts with network programming by implementing a pseudo-random number generator, a simple XOR-based encryption mechanism and a bidirectional TCP communication.

## Objectives

The main objectives of this practical work are:

* implement a pseudo-random number generator (PRNG);
* use the PRNG to generate a pseudo-random byte stream;
* encrypt and decrypt messages using XOR;
* encode encrypted data using Base64;
* establish a TCP connection between two computers;
* allow both users to send and receive messages;
* handle sending and receiving concurrently.

## Architecture

The communication is established between two computers.

```text
PC 1                                      PC 2

Message                                   Message
   |                                         ^
   v                                         |
Encryption                                Decryption
   |                                         ^
   v                                         |
 Base64                                    Base64
   |                                         ^
   v                                         |
Socket  <========== TCP ==========>        Socket
   |                                         ^
   v                                         |
Reception                                 Reception
```

PC 1 acts as the TCP server and PC 2 acts as the TCP client when establishing the connection.

Once the connection has been established, both computers can send and receive messages.

## PRNG

The project uses a Linear Congruential Generator.

The internal state is updated according to:

```text
x(n+1) = (a * x(n) + c) mod n
```

The parameter `n` is set to `256`.

The key is used to initialize the internal state of the generator.

A new PRNG value is generated for each byte of the message.

## Encryption

The message is first converted to bytes using UTF-8.

Each byte is then combined with a PRNG value using XOR:

```text
encrypted_byte = clear_byte XOR PRNG_value
```

The resulting encrypted bytes are encoded using Base64 before being sent through the TCP connection.

The receiver performs the reverse operations:

```text
Base64 decoding
       ↓
Encrypted bytes
       ↓
XOR with the PRNG stream
       ↓
Original bytes
       ↓
UTF-8 decoding
       ↓
Clear message
```

Because XOR is reversible:

```text
(A XOR K) XOR K = A
```

the original message can be reconstructed when the same PRNG stream is used.

## Bidirectional communication

Each program uses a dedicated thread for receiving messages.

The main thread remains available for user input and message transmission.

As a result, both participants can communicate in both directions without waiting for the other participant to finish sending.

Example:

```text
PC 1  -------------------->  PC 2
      "Hello"

PC 1  <--------------------  PC 2
      "Hello PC 1"
```

### `pc1.py`

TCP server.

The program waits for an incoming connection on port `5000`.

### `pc2.py`

TCP client.

The program connects to the IP address of PC 1 on port `5000`.

## Requirements

* Python 3.x
* Two computers connected to the same network
* VS Code or another Python IDE

Only Python standard library modules are used:

```python
socket
threading
base64
```

No external Python package is required.

## How to run

### PC 1

Start the server:

```bash
python pc1.py
```

The program waits for an incoming connection:

```text
PC 1 - SERVEUR
En attente d'une connexion sur le port 5000...
```

### PC 2

First, find the IPv4 address of PC 1.

On Windows:

```powershell
ipconfig
```

Then set the address in `pc2.py`:

```python
HOST = "IP_ADDRESS_OF_PC1"
```

For example:

```python
HOST = "172.20.10.2"
```

Then start:

```bash
python pc2.py
```

When the connection is established, both users can exchange messages.

## Example

PC 1:

```text
> Bonjour
[ENVOYÉ] Bonjour
```

PC 2:

```text
[REÇU] Bonjour
```

The same process works in the opposite direction.


## Learning outcomes

This practical work provides hands-on experience with:

* Python object-oriented programming;
* pseudo-random number generation;
* XOR-based encryption;
* Base64 encoding and decoding;
* TCP sockets;
* client/server communication;
* concurrent message reception;
* basic cryptographic design considerations.

## Context

Academic practical work completed as part of an engineering course in cryptography and cybersecurity.

