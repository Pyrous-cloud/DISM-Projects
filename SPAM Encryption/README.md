# SPAM Encryption
Implementating encryption and other cryptographic principles for SPAM file transfer from client to server (day_end.csv) and server to client (menu_today.txt), with my classmates Noel and Jay Kai.

<br />

## Setup
1. Change filepath base on preference or leave it to run as relative path
2. pip3 install coloroma
3. Download C++ Build Tools and tick the first 2 optional options from Visual Studio Build Tools
4. pip install pycryptodomex --no-binary:all:
6. Run server and then client (python3 <path to file>)
7. Use credentials username:hello, password:hello and passphrase:secretclient 

<br />

## Other info
1. If failed authenthication check 3 times, user will be kicked out of program and failed attempt will be written to error log with relevant information
2. Else, user is brought to option page where user can choose to get menu or send day-end file

<br />

## Contributions
### Hao xuan
1. Public key management 
2. Encryption of day end using RSA and AES
3. Digital signature for day end and menu

### Jay Kai
1. Login function
2. Error log

### Noel
1. All GUI functions
