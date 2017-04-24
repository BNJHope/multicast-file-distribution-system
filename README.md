# Multicast File Distribution System
The first practical in the Third Year Data Communications and Networks module. It is a multicast file distribution system implemented in Python 3. File blocks are transferred over UDP and then control messages
to determine which packets were missed in transfer etc. are transmitted over TCP.

Only tested on internal network at the University of St Andrews Department of Computer Science - the system implementation is described in the report file.

Build & Run
----------------
To run the client, run

$ python3 ClientTest.py

and this will set up the Client who will listen to any incoming connections from the server infinitely.

To send a file to as many available clients (currently applies to given list of school machines but modifications can be made) then run

$ python3 ServerTest.py test.txt

to send test.txt to all available clients.
