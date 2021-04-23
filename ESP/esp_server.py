# Importing relevant modules
import json, os
import socket
import threading, time, random
from datetime import datetime

# Opening file using json
try:
    # Services file
    services_file = open('C:.\\esp_data\\services.json')
    services = services_file.read()
    services = json.loads(services)
    services = json.dumps(services)
    services_file.close()
    # User data file
    users_file = open('C:.\\esp_data\\user.json')
    users = users_file.read()
    users = json.loads(users)
    users_file.close()
except:
    print('The file cannot be found or there is an error with the file...')
    os._exit(1)

# Getting a socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 8089))
serversocket.listen(5)        # become a server socket, maximum 5 pending connections
print('Server starts listening... ')
client= 0
stopFlag=False


# Function to decrypt
def decipher(ciphertext):
    plaintext = ''
    for char in ciphertext:
        if char not in "'}{[]":
            plaintext += chr(ord(char) - 3)
        else:
            plaintext += char
    return plaintext


# Cipher to encrypt data
def cipher(data):
    ciphertext = ''
    for char in data:
        if char not in "'}{[]":
            ciphertext += chr(ord(char) + 3)
        else:
            ciphertext += char
    return ciphertext


# Function for handling connections
def handler(con,client_addr):
  con.settimeout(300.0)
  idle_count = 0
  
  while True:
    try:
      buf = con.recv(1000).decode()          # decode the bytes into printable str
      if len(buf) > 0:
        idle_count = 0
        # Get the time and date everytime user communicates with server
        today_date = datetime.now()
        today_date = today_date.strftime('%d/%m/%Y %H:%M:%S')
        buf_list = buf.split('=')
        # Printing connection info
        con_info = f'User from: {client_addr} : INSTRUCTION={buf_list[0]} : TIME={today_date}'
        print(con_info)
        
        # Write the information into the log and if there is a login write into alive clients
        try:
          log_file = open('C:.\\esp_data\\log.txt', 'a')
          log_file.write(con_info + '\n')
          log_file.close()
          alive_clients_file = open('C:.\\esp_data\\alive_clients.json')
          alive_clients = alive_clients_file.read()
          alive_clients = json.loads(alive_clients)
          alive_clients_file.close()
        except:
          print('The file cannot be found or there is an error with the file...')
          os._exit(1)

        # Send the services
        if buf_list[0] == 'getser':
          con.send(services.encode())

        # User requests to login, code for validation of login
        elif buf_list[0] == 'login':
          if buf_list[1] in users:
              if buf_list[1] not in alive_clients:
                if buf_list[2] == users[buf_list[1]]['passwd']:
                  con.send('found'.encode()) 
                  time.sleep(1.5)
                  user_data = users[buf_list[1]]
                  user_data = json.dumps(user_data)
                  user_data = cipher(user_data)
                  con.send(user_data.encode())
                  try:
                    alive_clients[buf_list[1]] = True
                    alive_clients_file = open('C:.\\esp_data\\alive_clients.json', 'w')
                    alive_clients_file.write(json.dumps(alive_clients, indent=4))
                    alive_clients_file.close()
                  except:
                    print('The file cannot be found or there is an error with the file...')
                    os._exit(1)
                else:
                  con.send('wrongpass'.encode())
              else:
                con.send('usrins'.encode())
          elif not buf_list[1]:
              con.send('nil'.encode())
          else:
              con.send('notfound'.encode()) 
        # Client requests for a invoice number, server generates one and send back
        elif buf_list[0] == 'geninv':
          while True:
            inv_num = str(random.randint(0, 9999999999999))
            users_names = list(users.keys())
            for user in users_names:
              if users[user]['inv_num'] == inv_num:
                break
            else:
              con.send(inv_num.encode())
              break
        # Client registers for a new user, server checks if username exists
        elif buf_list[0] == 'regnam':
          if buf_list[1] in users:
            con.send('namexi'.encode())
          elif not buf_list[1]:
            con.send('nil'.encode())
          else:
            con.send('sucreg'.encode())
        # Client exits the program, server writes new data into the relevant files
        elif buf_list[0] == 'wrinew':                       
          buf_list[2] = decipher(buf_list[2])
          buf_list[2] = json.loads(buf_list[2])
          users[buf_list[1]] = buf_list[2]
        
          # Opening file using json
          try:
              # User data file
              users_file = open('C:.\\esp_data\\user.json', 'w')
              users_file.write(json.dumps(users, indent=4))
              users_file.close()

              # Remove the client from alive clients
              if buf_list[1] in alive_clients:
                del(alive_clients[buf_list[1]])
              alive_clients_file = open('C:.\\esp_data\\alive_clients.json', 'w')
              alive_clients_file.write(json.dumps(alive_clients, indent=4))
              alive_clients_file.close()
          except:
              print('The file cannot be found or there is an error with the file...a')
              os._exit(1)
      else:
        break 
    # Code for timeout
    except Exception as inst:
      if str(inst) == 'timed out':
        idle_count = idle_count + 1
        print('handler {} time out: idle count is {}'.format(str(client_addr),idle_count))
      if stopFlag or idle_count > 5 or (str(inst) != 'timed out'):
        break
  
  # If client timeout, remove from alive clients file
  try:
    if buf_list[1] in alive_clients:
      del(alive_clients[buf_list[1]])
    alive_clients_file = open('C:.\\esp_data\\alive_clients.json', 'w')
    alive_clients_file.write(json.dumps(alive_clients, indent=4))
    alive_clients_file.close()
  except:
    print('Write new data failed as there was no login before timeout')

  con.close()
  print('handler for {} is terminated'.format(str(client_addr)))
  return  


# main program starts here
while True:
  try:
    connection, address= serversocket.accept()
    print('start a new connection for {}'.format(str(address)))

    #setup and start a new thread to run an instance of handler()
    t = threading.Thread(target=handler, args=(connection,address))
    t.start()
  except Exception:
    # network error.
    break
  except KeyboardInterrupt:
    # user pressed control c to stop the server
    break
# end of while loop

stopFlag = True               # This will trigger all the active client threads to stop
serversocket.close()
print('Server is halted.')
