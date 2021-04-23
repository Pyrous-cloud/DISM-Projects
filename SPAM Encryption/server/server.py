# Server program
import datetime
import sys, traceback
import pickle
import os
import time
from Cryptodome.Cipher import PKCS1_OAEP, PKCS1_v1_5, AES  
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Signature import pkcs1_15
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from colorama import Fore, init

# Reset colour after everytime when you use it
init(autoreset=True)

cmd_GET_MENU = "GET_MENU"
cmd_END_DAY = "CLOSING"
default_menu = ".\\server\\menu_today.txt"
default_save_base = "result-"
passphrase = "secretserver"

# RKCS1_OAEP cipher is based on RSA - it is described in RFC8017 (Done by Hao Xuan)
# It is a asymmetric cipher.
# Encryption requires the public key of the key pair
#Decryption requires the private key of the key pair
header="""A Simple Program using the combination of RSA and AES to decrypt an encrypted text file with the size larger than key size.
Using a RSA private key and a stored AES key.
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
    data = open(f".\\server\\menu_today.txt","rb").read() # hash the data from file
    digest=SHA256.new(data)
    print("digest:")
    for b in digest.digest():
        print("{0:02x}".format(b),end="")
    print("\n")
    pri_key_content=open(".\\server\\keys\\server_private.der","rb").read() # get the private key to sign
    pri_key=RSA.import_key(pri_key_content, passphrase=passphrase) # generate signature from private key and hash
    signature = pkcs1_15.new(pri_key).sign(digest)
    return signature


# Function to verify signature (Done by Hao Xuan)
def verify_sign(signature, plain_text):
    print("\nVerifying signature")
    digest=SHA256.new(plain_text) # hash the decrypted text
    print("digest:")
    for b in digest.digest():
        print("{0:02x}".format(b),end="")
    print("\n")
    pub_key_content=open(".\\server\\keys\\client_public.pem","rb").read() # get the client public key
    pub_key=RSA.import_key(pub_key_content)
    # Verify the signature
    try:
        pkcs1_15.new(pub_key).verify(digest, signature)
        print(Fore.GREEN + 'Signature is valid')
    except(ValueError,TypeError):
        print(Fore.RED + "The Signature is invalid")
        print(Fore.RED + "Please ask for menu again!")


# Function using RSA and AES to decrypt (Done by Hao Xuan)
# Uses the signature as a parameter so plaintext can be hashed and check the signature after decryption
def RSAAES_decrypt(signature):
    try:
        print(header)
        pri_key_content=open(".\\server\\keys\\server_private.der","rb").read()
        pri_key=RSA.import_key(pri_key_content, passphrase=passphrase)
        print("Done importing the private key")  
        keysize=pri_key.size_in_bytes()
        print("Decrypting the file content with the private key")
        data=open(filename,"rb").read()
        print(f"data chunk size; {len(data)}")
        # can use either PKCS1_V1_5 or PKCS1_OAEP cipher (different in padding scheme)
        # recommend to use PKCS1_OAEP instead of PKCS1_V1_5 to avoid chosen_cipher_text_attack
        #cipher = PKCS1_v1_5.new(pub_key)
        rsa_cipher = PKCS1_OAEP.new(pri_key)
        if len(data) > keysize:   # encrypted file will be in the mulitples of the keysize.
            # need to decrypt the data in with AES
            enc_payload = pickle.loads(data)
            if type(enc_payload) != ENC_payload:
                raise RuntimeError("Invalid encrypted file")
            aes_key=rsa_cipher.decrypt(enc_payload.enc_session_key) # retreive and decrypt the AES key
            aes_cipher = AES.new(aes_key,AES.MODE_CTR,iv=enc_payload.aes_iv)
            plain_text = unpad(aes_cipher.decrypt(enc_payload.encrypted_content), AES.block_size)
        else:    
            plain_text = rsa_cipher.decrypt(data)
            # now save the encrypted file
        new_filename = filename + "_day_end.dat"
        out_bytes=open(f"{new_filename}","wb").write(plain_text)
        verify_sign(signature, plain_text)
        print(f"\nWriting new file, total of {out_bytes} bytes written to {new_filename}")                
    except:
        print("Opps, the passphrase could be incorrect")
        traceback.print_exc(file=sys.stdout)


def process_connection( conn , ip_addr, MAX_BUFFER_SIZE):
    global filename
    blk_count = 0
    net_bytes = conn.recv(MAX_BUFFER_SIZE)
    dest_file = open(".\\server\\temp","w")
    while net_bytes != b'':
        if blk_count == 0: #  1st block
            usr_cmd = net_bytes[0:15].decode("utf8").rstrip()
            if cmd_GET_MENU in usr_cmd: # ask for menu
                signature = sign_file()
                src_file = open(default_menu,"rb")
                while True:
                    read_bytes = src_file.read(MAX_BUFFER_SIZE)
                    if read_bytes == b'':
                        break
                    conn.send(read_bytes + b"|||" + signature)
                src_file.close()
                print("Processed SENDING menu")
                return
            elif cmd_END_DAY in usr_cmd: # ask for to save end day order
                now = datetime.datetime.now()
                filename = ".\\server\\" + default_save_base +  ip_addr + "-" + now.strftime("%Y-%m-%d_%H%M")
                dest_file = open(filename,"wb")
                dest_file.write( net_bytes[ len(cmd_END_DAY): ] )  # remove the CLOSING header
                blk_count = blk_count + 1
        else:  # write other blocks
            net_bytes = conn.recv(MAX_BUFFER_SIZE)
            # Receive data and split
            if net_bytes != b'':
                data_list = net_bytes.split(b"|||")
                signature = data_list[1]
                dest_file.write(data_list[0])
            
    # last block / empty block
    dest_file.close()
    # If it is command end day need to decrypt the file received
    if cmd_END_DAY in usr_cmd:        
        RSAAES_decrypt(signature) # decrypt and verify the digital signature
    print("Deleting encrypted file")
    os.remove(filename) # Remove encrypted file after saving the decrypted one
    print(Fore.GREEN + "Processed CLOSING done")


def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):
    process_connection( conn, ip, MAX_BUFFER_SIZE)
    conn.close()  # close connection
    print('Connection ' + ip + ':' + port + " ended")


def start_server():
    import socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')
    try:
        soc.bind(("127.0.0.1", 8888))
        print('Socket bind complete')
    except socket.error as msg:
        import sys
        print('Bind failed. Error : ' + str(sys.exc_info()))
        print( msg.with_traceback() )
        sys.exit()
    #Start listening on socket
    soc.listen(10)
    print('Socket now listening')
    # for handling task in separate jobs we need threading
    from threading import Thread
    # this will make an infinite loop needed for
    # not reseting server for every client
    while True:
        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        try:
            Thread(target=client_thread, args=(conn, ip, port)).start()
        except:
            print("Terible error!")
            import traceback
            traceback.print_exc()
    soc.close()

    
start_server()




