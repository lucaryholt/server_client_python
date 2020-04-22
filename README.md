# Server Client project made in Python

Made as a mandatory assignment in Tech.

### Implemented functionality
 - Three way handshake
 - Timeout timer on server
 - KeepAlive option on client
 - External config files
 - Option for maximum packages received per second
 - Debug mode


### Notes for the code:
#### General
 - Both client and server runs a handshake protocol before actual communication starts, if not performed properly by either part, the connection is terminated.
#### Client
 - Has a thread that receives data and passes it to variable outside thread. Rest of program can then read data from that variable.
 - Another thread that sends 'heartbeat' messages at a configurable interval.
#### Server
 - Has a thread that counts how many packages per minute and terminates connection if above configurable maximum.
 - Another thread that manages a configurable timeout tolerance and terminates connection if that tolerance is met.
#### External .py files
 - configReader.py: As name suggests it reads a config file, from a given key value and returns either a boolean, integer, float or string.
 - conPrint.py: Contains multiple methods that takes a string and prints that string in a colour. Makes it easier to read the output.
