# Create a electronic services & protection system

# Importing relevant modules
import json, os, getpass, datetime, time, hashlib, random, re
from colorama import Fore, Back, Style, init
from datetime import date, datetime, timedelta
import socket

# Resetting colours after every print
init(autoreset=True)

# Connect to server
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "localhost"
clientsocket.connect((host, 8089))

clientsocket.send('getser'.encode())
services = clientsocket.recv(1000).decode()
services = json.loads(services)
user_data = {}    

# Getting todays date and the expiry date if user buys today
today_date = date.today()
expiry_date = (date.today()+ timedelta(364)).strftime("%d/%m/%Y")

# Function for user menu
def user_menu():
    # Making the cart global incase user has old cart to sync
    global services_added
    services_added = []
    while True:
        print()
        print('=' * 54)
        print('Welcome to Electronic Services & Protection User Menu:')
        print('=' * 54)
        print('\n1. Login')
        print('2. Register\n')

        # Asking for user input
        user_input = input('Please enter your choice of action (ENTER to exit): ').strip()

        # Validation for user input
        if (user_input in '12') and (len(user_input) <= 1):
            # Running the selected option
            if user_input == '1':
                # Runs login
                success_log = login()
                # If login is successful checks for old cart
                if success_log == True:
                    if user_data['cart']:
                        services_added = user_data['cart']
                        print(Fore.GREEN + 'Syncing old cart...')
                        time.sleep(1.5)
                    menu()
                    break
            elif user_input == '2':
                # Runs register
                success_reg = register()
                if success_reg:
                    menu()
                    break
            else:
                break
        else:
            print(Fore.RED + 'You have entered an invalid input, enter an index in the range from 1-2')
            time.sleep(1.5)


# Function for users that want to register
def register():
    # Make username global
    global user_name
    global user_data
    while True:
        # Asking for username
        user_name = input('Enter your username (ENTER to exit): ')
        # Formats information and sends to server for validation
        user_info = f'regnam♣{user_name}'
        if '♣' in user_name:
            print(Fore.RED + 'Invalid character detected, please try again')
            time.sleep(1.5)
            pass
        try:
            clientsocket.send(user_info.encode())
            ibuf = clientsocket.recv(255).decode()
        except ConnectionAbortedError:
            print(Fore.RED + 'You have timeout due to reaching the max time of 10 minutes')
            os._exit(1)
        
        # Checks if user exists and the length is > 0
        if ibuf == 'sucreg':
            while True:
                # Getting password
                input_passwd = getpass.getpass()
                regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
                # Validation and creating new user data
                if re.findall(regex, input_passwd):
                    user_data = {}
                    user_data['inv_num'] = ''
                    encoded_pass = hashlib.sha256(input_passwd.encode('utf-8')) 
                    hashed_pass = encoded_pass.hexdigest()
                    user_data['passwd'] = hashed_pass
                    user_data['vip'] = False
                    user_data['cart'] = []
                    return True
                else:
                    print(Fore.RED + 'The password must contain 1 letter, 1 number and 1 special character and > 8 chars\n')
                    time.sleep(1.5)
            break
        elif ibuf == 'namexi':
            print(Fore.RED + 'The user already exists\n')
        elif ibuf == 'nil':
            break
        time.sleep(1.5)


# Function for existing users to log in
def login():
    # Make user data global
    global user_data
    global user_name
    while True:
        # Asking for username
        user_name = input('Enter your username (ENTER to exit): ')
        if not user_name:
            break
        input_passwd = getpass.getpass()
        encoded_pass = hashlib.sha256(input_passwd.encode('utf-8'))
        hashed_pass = encoded_pass.hexdigest()
        user_info = f'login♣{user_name}♣{hashed_pass}'
        obuf = user_info.encode() # convert msg string to bytes
        try:
            clientsocket.send(obuf)
            ibuf = clientsocket.recv(255).decode()
        except ConnectionAbortedError:
            print(Fore.RED + 'You have timeout due to reaching the max time of 10 minutes')
            os._exit(1)
        
        
        # Checks if user exists
        if ibuf == 'found':
            print(Fore.GREEN + 'Login successful, syncing data...\n')
            user_data = clientsocket.recv(1000).decode()
            user_data = decipher(user_data)
            user_data = json.loads(user_data)
            
            # Run function to remove any subscription that has expired
            remove_expired()
            # User menu for login
            while True:
                print('=' * (50 + len(user_name)))
                print(f'Welcome back {user_name} to Electronic Services & Protection:')
                print('=' * (50 + len(user_name)))
                print('\n1. Check invoice')
                print('2. Check membership')
                print('3. Change password\n')

                # Asking for user input
                user_input = input('Enter your choice of action (ENTER to exit to shop): ').strip()

                # Validation and running selected choice
                if (user_input in '123') and (len(user_input) <= 1):
                    if user_input == '1':
                        check_invoice()
                    elif user_input == '2':
                        if user_data['vip'] == True:
                            print(Fore.GREEN + 'You are a member\n')
                            time.sleep(1.5)
                        else:
                            print(Fore.RED + 'You are not a member\n')
                            time.sleep(1.5)
                    elif user_input == '3':
                        edit_pass()
                    else:
                        break
                else:
                    print(Fore.RED + 'You have entered an invalid input, enter an index in the range from 1-4\n')
                    time.sleep(1.5)

            return True
        elif ibuf == 'notfound':
            print(Fore.RED + 'User not found, please try again\n')
        elif ibuf == 'wrongpass':
            print(Fore.RED + 'Password is incorrect, try again\n')
        elif ibuf == 'usrins':
            print(Fore.RED + 'User is currently logged in, please check again\n')
        elif ibuf == 'nil':
            break
        time.sleep(1.5)



# Function to edit password
def edit_pass():
    while True:
        # Asking for new password
        user_input = getpass.getpass('New password (ENTER to exit): ')
        regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
        # Validation for password
        if re.findall(regex, user_input):
            # Hashes password and changes to new
            encoded_pass = hashlib.sha256(user_input.encode('utf-8'))
            hashed_pass = encoded_pass.hexdigest()
            user_data['passwd'] = hashed_pass
            print(Fore.GREEN + f'Your password has been changed to {user_input}\n')
            time.sleep(1.5)
            break
        elif user_input:
            print(Fore.RED + 'The password must contain 1 letter, 1 number and 1 special character and > 8 chars\n')
            time.sleep(1.5)
        else:
            break

# Function to print invoice
def check_invoice():
    # Make username global
    global user_name
    # If user has subscription print invoice
    if len(user_data.keys()) > 4:
        if user_data['inv_num']:
            inv_num = user_data['inv_num']
        else:
            # Asks server to generate invoice number and send back
            try:
                clientsocket.send('geninv'.encode())
                inv_num = clientsocket.recv(255).decode()
            except ConnectionAbortedError:
                print(Fore.RED + 'You have timeout due to reaching the max time of 10 minutes')
                os._exit(1)
            user_data['inv_num'] = inv_num

                
        # Creating string for invoice and adding information
        invoice = f'''
 ___________________________________
|        ESP service invoice        |
|     invoice no: {inv_num:<13}     |'''

        index = 4
        while index < (len(user_data.keys())):
            expiry = (list(user_data.keys())[index])
            start = (datetime.strptime(expiry, '%d/%m/%Y') - timedelta(364)).strftime('%d/%m/%Y')
            price = 0
            for subscription in user_data[expiry]:
                sub_price = str(services[subscription]) + 'k/year'
                invoice += f'\n| {subscription:<20} {sub_price:<12} |'
                price += services[subscription]
            if user_data['vip']:
                price *= 0.8
            price = round(price, 1)
            price = str(price) + 'k/year'
            invoice += f'\n| start: {start}                 |'
            invoice += f'\n| expiry: {expiry}                |'
            invoice += f'\n| total: {price:<13}              |'
            index += 1
            invoice += '\n|                                   |'

        invoice += '\n-------------------------------------\n'
        print(invoice)
        time.sleep(4)
    else:
        print(Fore.RED + 'You have not subscribed to anything yet\n')
        time.sleep(1.5)


# Function to remove expired subscriptions
def remove_expired():
    to_be_deleted = []
    if len(user_data.keys()) > 4:
        for i in range(4, len(user_data.keys())):
            expiry = (list(user_data.keys())[i])
            # Convert key from string to date object so that can compare
            if datetime.strptime(expiry, '%d/%m/%Y').date() < today_date:
                to_be_deleted.append(expiry)
        for date in to_be_deleted:
            del(user_data[date])


# Function to check if user has already subbed to a service
def already_subbed(service_chosen):
    subbed_service = []
    if len(user_data.keys()) > 4:
        for i in range(4, len(user_data.keys())):
            expiry = (list(user_data.keys())[i])
            for service in user_data[expiry]:
                subbed_service.append(service)
    if service_chosen in subbed_service:
        return True


# Main program
# Menu function to display menu
def menu():
    # Main program loop
    while True:
        print()
        print('=' * 44)
        print('Welcome to Electronic Services & Protection:')
        print('=' * 44)
        print('\n1. Display our list of services')
        print('2. Search for service(s)')
        print('3. Display/Edit added services')
        print('4. Payment\n')

        # Asking for user input
        user_input = input('Please input your choice of action (ENTER to exit): ').strip()

        # Validation of input
        if (user_input in '1234') and (len(user_input) <= 1):
            # Running the selected option
            if user_input == '1':
                choose_services()
            elif user_input == '2':
                search_service()
            elif user_input == '3':
                edit_cart()
            elif user_input == '4':
                success_pay = caculate_price()
                if success_pay == True:
                    break
            else:
                exit()
                break
        else:
            print(Fore.RED + 'You have entered an invalid input, enter an index in the range from 1-4')
            time.sleep(1.5)
        

# Function to print the services that can be choose from and allows user to add to cart
def choose_services(choose_from=list(services.keys())):   
    global services_added
    while choose_from:
        # Printing the list of services
        print('Yes, we have the following service(s):')
        for i, service in enumerate(choose_from):
            print(f'{i + 1}. {service:20} : \t${services[service]}k/year')
        
        # User input
        user_input = input('\nEnter the service you would like to add using its index (ENTER to exit): ').strip()

        # Adding service using index and validation
        if user_input.isnumeric():
            if (0 < int(user_input) <= len(choose_from)):
                if (choose_from[int(user_input) - 1] not in services_added):
                    if (already_subbed(choose_from[int(user_input) - 1])) == True:
                        print(Fore.RED + 'You have already subbed to this service\n')
                    else:
                        services_added.append(choose_from[int(user_input) - 1])
                        print(Fore.GREEN + f'The service {choose_from[int(user_input) - 1]} has been added\n')
                else:
                    print(Fore.RED + 'You have already selected this service\n')
            else:
                print(Fore.RED + f'The index is out of range, enter an index in the range from 1-{len(choose_from)}\n')
        # If there is input but not numeric it is invalid
        elif user_input:
            print(Fore.RED + f'You have entered an invalid input, enter an index in the range from 1-{len(choose_from)}\n')
        # ENTER to exit
        else:
            break 
        time.sleep(1.5)
    # Tells user if there is no services
    else:
        print('There are currently no services')


# Function to search for a service 
def search_service():
    # List to store services that are found
    found_services = []
    # Count to keep track of how many services are found
    count = 0

    # User input
    user_input = input('Please input service to search (ENTER to show all): ').strip()
    print()

    # If service is found append to found_services and increment count
    for service in services.keys():
        if user_input.upper() in service.upper():
            found_services.append(service)
            count += 1

    # Informs the user if no services are found or runs the choose_services function 
    # for users to choose the services found
    if count == 0:
        print(Fore.RED + 'Sorry we do not have that service currently')
        time.sleep(1.5)
    else:
        choose_services(found_services)


# Function to edit the cart
def edit_cart():
    global services_added
    while services_added:

        # Printing the services in the cart
        print('Your cart currently contains:')
        for i, service in enumerate(services_added):
            print(f'{i + 1}. {service:20} : \t${services[service]}k/year')

        # User input
        user_input = input('\nEnter the service to remove (ENTER to exit): ').strip()

        # If user removes using index
        if (user_input.isnumeric()) and (0 < int(user_input) <= len(services_added)):
            print(Fore.GREEN + f'{services_added[int(user_input) - 1]} has been removed from the cart\n')
            del(services_added[int(user_input) - 1])
        # If input is incorrect
        elif user_input:
            print(Fore.RED + f'You have entered an invalid input, enter an index in the range from 1-{len(services_added)}\n')
        # ENTER to exit
        else:
            break
        time.sleep(1.5)
    # Tells user if cart is empty
    else:
        print(Fore.RED + 'Your cart is empty')
        time.sleep(1.5)


# Function to caculate the total price of subscription
def caculate_price():
    global services_added
    if services_added:
        price = 0

        # Add the price for each service
        for service in services_added:
            price += services[service]
        
        # Print the price of subscription
        while True:
            # Asks for user input
            user_input = input('Would you like to pay now y/n: ').strip()

            # Validation of input 
            if (user_input.upper() in 'YN') and (len(user_input) == 1):
                if user_input.upper() == 'Y':
                    user_data['cart'] = []
                    # Checks if user has vip or if the price is > 5k so can give user vip
                    if user_data['vip']:
                        price *= 0.8
                        print(Fore.BLACK + Back.CYAN + 'The price has been discounted due to your membership')
                    elif price > 5:
                        user_data['vip'] = True
                        print(Fore.BLACK + Back.CYAN + 'Because you spent more than 5k you are now a member and get 20 percent off all purchases (including previous transaction)')
                        price *= 0.8
                    
                    # Round price to 1d.p.
                    price = round(price, 1)
                    print(f'Your subscription will be a total of : ${price:}k/year')

                    # Checks if user bought other subscriptions in same day, if yes add to existing, if no create new key
                    try:
                        user_data[expiry_date] += services_added
                    except:
                        user_data[expiry_date] = services_added
                    # Function to print invoice
                    check_invoice()
                    # Other information
                    print(Fore.BLACK + Back.CYAN + 'Our store has a no refund policy, if you have any feedback please contact our customer service')
                    print(Fore.BLACK + Back.CYAN + 'The discounted price is only reflected in total')
                    return True
                else:
                    print('If you would like to save your cart, remember to do it when exiting')
                    return False
            print(Fore.RED + 'Invalid input, please try again\n')
            time.sleep(1.5)
    else:
        print(Fore.RED + 'Your cart is empty')
        time.sleep(1.5)

def exit():
    # Make username global
    global user_name
    if services_added:
        while True:
            # Asks for user input
            user_input = input('You have items in your cart would you like to save them y/n: ').strip()

            if (user_input.upper() in 'YN') and (len(user_input) == 1):
                # Saves the cart
                if user_input.upper() == 'Y':
                    user_data['cart'] = services_added
                    break
                # Discards the cart
                else:
                    user_data['cart'] = []
                    break
            print(Fore.RED + 'Invalid input, please try again\n')
            time.sleep(1.5)


# Cipher to encrypt data
def cipher(data):
    ciphertext = ''
    for char in data:
        if char not in "'}{[]":
            ciphertext += chr(ord(char) + 3)
        else:
            ciphertext += char
        
    return ciphertext


# Function to decipher encrypted data
def decipher(ciphertext):
    plaintext = ''
    for char in ciphertext:
        if char not in "'}{[]":
            plaintext += chr(ord(char) - 3)
        else:
            plaintext += char
    
    return plaintext


# Run the menu function
user_menu()

# If there is user data, write the new data by connecting to server
if user_data:
    user_data = json.dumps(user_data)
    user_data = cipher(user_data)
    new_info = f'wrinew♣{user_name}♣{user_data}'
    
    try:
        clientsocket.send(new_info.encode())
    except ConnectionAbortedError:
        print(Fore.RED + 'You have timeout due to reaching the max time of 30 minutes, new data will not be synced')
        os._exit(1)

# Close connection
clientsocket.close()



