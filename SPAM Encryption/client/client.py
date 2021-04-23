# Client program
# GUI done by Noel
import socket
import sys, traceback
import pickle
import os
import time
import csv
from datetime import datetime, date, timedelta
import getpass
import hashlib
import tkinter
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import PKCS1_OAEP, PKCS1_v1_5, AES  
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Signature import pkcs1_15
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from colorama import Fore, init

# Reset colour after everytime when you use it
init(autoreset=True)

# default 
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8888        # The port used by the server
failedCount = 0
cmd_GET_MENU = b"GET_MENU"
cmd_END_DAY = b"CLOSING"
menu_file = ".\\client\\menu_today.txt"
return_file = ".\\client\\day_end.csv"
#passphrase is secretclient
failedCount = 0
passphrase = "5bc7bf58907ea50543c8326f0b552ed5def3d32d0cf9be0d3b83a0e6cb18b81c735e686b3565a9cf915a445b1a88e72192d3d0ae88e55f734ae8fdb5a392dc97"

# RKCS1_OAEP cipher is based on RSA - it is described in RFC8017 (Done by Hao Xuan)
# It is a asymmetric cipher.
# Encryption requires the public key of the key pair
# Decription requires the private key of the key pair
header="""A Simple Program using the combination of RSA and AES to encrypt a text file with the size larger than the key size.
Using a public key and a randomly generated AES key.
""" 
class ENC_payload:
    # A data class to store a encrypted file content.
    # The file content has been encrypted using an AES key.
    # The AES key is encrypted by a public key and stored in the enc_session_key instance attribute. 
    def __init__(self):
        self.enc_session_key=""
        self.aes_iv = ""
        self.encrypted_content=""
RSA_OVERHEAD = 66 # assume there is a overhead of 66 bytes per RSA encrypted block. when using OAEP with sha256


# Function to sign file (Done by Hao Xuan)
def sign_file():
    print(Fore.GREEN + "\nSigning file before transmission")
    data = open(".\\client\\day_end.csv","rb").read() # read the data and hash
    digest=SHA256.new(data)
    print("digest:")
    for b in digest.digest():
        print("{0:02x}".format(b),end="")
    print("\n")
    pri_key_content=open(".\\client\\keys\\client_private.der","rb").read() # get the private key to sign
    pri_key=RSA.import_key(pri_key_content, passphrase=passphrase)
    signature = pkcs1_15.new(pri_key).sign(digest) # generate signature with hash and private key
    return signature


# Function to verify signature (Done by Hao Xuan)
def verify_sign(signature):
    print("\nVerifying signature")
    data = open(".\\client\\menu_today.txt", "rb").read() # read the file received and hash it
    digest=SHA256.new(data)
    print("digest:")
    for b in digest.digest():
        print("{0:02x}".format(b),end="")
    print("\n")
    pub_key_content=open(".\\client\\keys\\server_public.pem","rb").read() # import server public key
    pub_key=RSA.import_key(pub_key_content)
    # Check if signature is valid
    try:
        pkcs1_15.new(pub_key).verify(digest, signature)
        print(Fore.GREEN + 'Signature is valid')
        verify_window = tkinter.Toplevel(login_window)
        verify_window.title("Verification Success")
        verify_window.geometry("400x300")
        tkinter.Label(verify_window,text="").pack()
        tkinter.Label(verify_window,text="Verification Success!", fg="green").pack()
        tkinter.Button(verify_window,text="Ok",bd = "4",width="15",pady="3",command=lambda:[sys.exit(0)]).pack()
    except(ValueError,TypeError):
        print(Fore.RED + "The Signature is invalid")
        print(Fore.RED + "Please ask for menu again!")
        verify_window = tkinter.Toplevel(login_window)
        verify_window.title("Verification Failed")
        verify_window.geometry("400x300")
        tkinter.Label(verify_window,text="").pack()
        tkinter.Label(verify_window,text="Verification Failed!", fg="red").pack()
        tkinter.Button(verify_window,text="Ok",bd = "4",width="15",pady="3",command=lambda:[sys.exit(0)]).pack()


# Function using RSA and AES to encrypt (Done by Hao Xuan)
def RSAAES_encrypt():
    try:
        print(header)
        pub_key_content=open(".\\client\\keys\\server_public.pem","r").read()
        pub_key=RSA.import_key(pub_key_content)
        print("Done importing the public key") 
        print(f"Public Key:\n{pub_key_content}") 
        print(f"keysize: {pub_key.size_in_bytes()}")
        print("Encrypting the file content with the public key")
        # can use either PKCS1_V1_5 or PKCS1_OAEP cipher (different in padding scheme)
        # recommend to use PKCS1_OAEP instead of PKCS1_V1_5 to avoid chosen_cipher_text_attack
        # rsa_cipher = PKCS1_v1_5.new(pub_key)
        rsa_cipher = PKCS1_OAEP.new(pub_key)
        data=open(return_file,"rb").read()
        print(f"data chunk size; {len(data)}")
        size_limit = pub_key.size_in_bytes() - RSA_OVERHEAD
        if len(data) > size_limit:
            # need to use AES to encrypt the file body.
            # The key being used will be encrypted by the RSA public key and store as part of the encrypted item
            aes_key = get_random_bytes(AES.block_size)
            aes_cipher = AES.new(aes_key,AES.MODE_CBC) #
            ciphertext = aes_cipher.encrypt(pad(data,AES.block_size))
            enc_payload = ENC_payload()
            enc_payload.enc_session_key = rsa_cipher.encrypt(aes_key) 
            enc_payload.aes_iv = aes_cipher.iv # retrieve the randomly generated iv value 
            enc_payload.encrypted_content=ciphertext
            encrypted=pickle.dumps(enc_payload) # serialize the enc_payload object into a byte stream.
        else:                 
            encrypted = rsa_cipher.encrypt(data)
            # now save the encrypted file
        out_bytes=open(".\\client\\encrypted_day_end.dat","wb").write(encrypted)
        print(f"Total of {out_bytes} bytes written to encrypted_day_end.dat")
    except:
        print("Opps")
        traceback.print_exc(file=sys.stdout)


# Get menu (Done by Hao Xuan)
def get_menu():
    menu_file = ".\\client\\menu_today.txt"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.connect((HOST, PORT))
        my_socket.sendall(cmd_GET_MENU )
        data = my_socket.recv(4096)
        data_list = data.split(b"|||")
        menu_file = open(menu_file,"wb")
        menu_file.write(data_list[0])
        menu_file.close()
        my_socket.close()
    print(Fore.GREEN + "\nReceived menu")  # for debugging use
    verify_sign(data_list[1])
    my_socket.close()


# Send day end information (Done by Hao Xuan)
def send_day_end():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as my_socket:
        my_socket.connect((HOST, PORT))
        my_socket.sendall(cmd_END_DAY)   
        time.sleep(0.5) # Prevent multiple transmissions from jamming
        RSAAES_encrypt() # Run function to encrypt
        signature = sign_file()
        temp = open(".\\client\\temp","wb")
        encrypted_file = open(".\\client\\encrypted_day_end.dat","rb")
        encrypted = encrypted_file.read()
        encrypted_file.close()
        temp.write(encrypted + b"|||" + signature)
        temp.close()
        out_file = open(".\\client\\temp","rb")
        file_bytes = out_file.read(1024) 
        while file_bytes != b'':
            my_socket.send(file_bytes)
            file_bytes = out_file.read(1024) # read next block from file
        out_file.close()
        my_socket.close()
        print("Deleting encrypted file")
        os.remove(".\\client\\encrypted_day_end.dat") # remove the encrypted file after transmission
        os.remove(".\\client\\temp")
    print(Fore.GREEN + 'Sent', repr(file_bytes))  # for debugging use
    send_window = tkinter.Toplevel(login_window)
    send_window.title("Send Success")
    send_window.geometry("400x300")
    tkinter.Label(send_window,text="").pack()
    tkinter.Label(send_window,text="Successfully Sent!", fg="green").pack()
    tkinter.Button(send_window,text="Ok",bd = "4",width="15",pady="3",command=lambda:[sys.exit(0)]).pack()
    my_socket.close()


def login_sucess():
    global sucess_window
    sucess_window = tkinter.Toplevel(login_window)
    sucess_window.title("Login Successful")
    sucess_window.geometry("400x300")
    tkinter.Label(sucess_window,text="").pack()
    tkinter.Label(sucess_window,text="Login Successful!", fg="green").pack()
    tkinter.Button(sucess_window,text="Ok",bd = "4",width="15",pady="3",command=lambda:[user_menu(),sucess_window.withdraw(),login_window.withdraw()]).pack()


def user_menu():
    user_window = tkinter.Toplevel(sucess_window)
    user_window.title("Menu")
    user_window.geometry("400x300")
    tkinter.Label(user_window,text="").pack()
    tkinter.Button(user_window,text="Get Menu File",fg ="green",bd = "4",width="30",pady="6",command=lambda:[get_menu(),user_window.withdraw()]).pack()
    tkinter.Label(user_window,text="").pack()
    tkinter.Button(user_window,text="Send Day end File",fg ="green",bd = "4",width="30",pady="6",command=lambda:[send_day_end(),user_window.withdraw()]).pack()


def failed_window():
    warning_window = tkinter.Toplevel(login_window)
    warning_window.title("Login Failed")
    warning_window.geometry("700x300")
    tkinter.Label(warning_window,text="").pack()
    tkinter.Label(warning_window,text="You have been logged out for failing to correctly enter your password 3 times.", fg="red").pack()
    tkinter.Label(warning_window,text="").pack()
    tkinter.Label(warning_window,text="If you are the account owner and you have forgotten your password, please reset it.", fg="red").pack()
    tkinter.Label(warning_window,text="").pack()
    tkinter.Label(warning_window,text="If you are NOT the account owner, the administrators have been informed and WILL investigate.", fg="red").pack()
    tkinter.Button(warning_window,text="Ok",bd = "4",width="15",pady="3",command=lambda:[sys.exit(0)]).pack()


# Check if credentials are correct (Done by Jay Kai)
def user_authenthicaton(username,password,passphrase_check):
    global passphrase, failedCount
    users = []
    logged_in = False
    try:
        with open(".\\client\\users.tsv", "r") as loginInfo: # read in user login info from external file
            my_reader = csv.reader(loginInfo, delimiter="\t")
            for row in my_reader:
                users.append(row)
    except:
        print(Fore.RED + "\nUser data unavailable. Exiting...") # exit program with error message if file not found
        sys.exit(0)

    userName = username.get().strip()
    passWord = password.get().strip()
    passWord = hashing(passWord)
    input_phrase =  passphrase_check.get().strip()
    for x in range(len(users)):
        if users[x][0] == userName and users[x][1] == passWord and hashing(input_phrase) == passphrase:
            print(Fore.GREEN + "\nLogin successful!")
            passphrase = input_phrase
            logged_in = True
            break
        else:
            failedCount+=1
            tkinter.Label(login_window,text=f"Login Failed. You have {3-failedCount} remaining attempts left.",fg="red").pack()
            print(failedCount)
            if failedCount == 3:
                errorLog = [userName, "Login", datetime.now().strftime(f"%H:%M:%S on %d/%m/%Y")]
                with open(".\\client\\error_logs.tsv", "a") as errorLogs: # output failed login attempt to external file
                    my_writer = csv.writer(errorLogs, delimiter="\t", lineterminator="\n")
                    my_writer.writerow(errorLog)
                login_window.withdraw()
                failed_window()
    if logged_in:
        login_window.withdraw()
        login_sucess()


# Allow user to choose desired action (Done by Jay Kai)
def user_choice():
    user_input = int(input("\nWhat is your choice: ").strip())
    # Display Choices for users
    while user_input not in [1,2]:
        user_input = input("Enter 1 or 2 only: ")
    if user_input == 1:
        get_menu()
    else: 
        send_day_end()


# Function to hash passwords for better security (Done by Jay Kai)
def hashing(passWord): 
    passWord = passWord.encode('utf-8')
    hashedPass = hashlib.sha512(passWord)
    return hashedPass.hexdigest()


# Login function to obtain login credentials (Done by Jay Kai)
def login():
    global login_window
    username_entry = tkinter.StringVar()
    password_entry = tkinter.StringVar()
    passphrase_entry = tkinter.StringVar()
    login_window = tkinter.Toplevel(window)
    login_window.title("Login")
    login_window.geometry("400x300")
    tkinter.Label(login_window,text="Please enter the login details:").pack()
    tkinter.Label(login_window,text="")
    tkinter.Label(login_window,text="Username:").pack()
    userName = tkinter.Entry(login_window, textvariable=username_entry)
    userName.pack()
    tkinter.Label(login_window,text="")
    tkinter.Label(login_window,text="Password").pack()
    passWord = tkinter.Entry(login_window, textvariable=password_entry,show="*")
    passWord.pack()
    tkinter.Label(login_window,text="")
    tkinter.Label(login_window,text="Passphrase:").pack()
    passPhrase = tkinter.Entry(login_window, textvariable=passphrase_entry,show="*")
    passPhrase.pack()
    tkinter.Label(login_window,text="").pack()
    tkinter.Button(login_window,text="Login",fg="green",bd = "4",width="15",pady="3",command=lambda:[user_authenthicaton(username_entry,password_entry,passphrase_entry)]).pack()


def main_screen():
    global window
    window = tkinter.Tk()
    window.geometry("400x250")
    window.title("ESP Service")
    tkinter.Label(window,text="Welcome to Outlet 1 @ Changi!", fg="green").pack()
    tkinter.Label(window,text="").pack()
    tkinter.Button(window,text="Login",fg="green",bd = "4",width="15",pady="3", command=lambda:[login(),window.withdraw()]).pack()
    window.mainloop()

    
main_screen()

print(Fore.GREEN + "\nProgram has ended") 
