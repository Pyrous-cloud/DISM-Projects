# Admin to configure esp

# Importing relevant modules
import os, json, time
from colorama import Fore, Back, Style, init

# Resetting colours after every print
init(autoreset=True)

# Opening file with services to read
try:
    services_file = open('C:.\\esp_data\\services.json')
    services = services_file.read()
    services = json.loads(services)
    services_file.close()
    users_file = open('C:.\\esp_data\\user.json')
    users = users_file.read()
    users = json.loads(users)
    users_file.close()
except:
    print('The file cannot be found or there is an error with the file...')
    os._exit(1)


# Function for editing services
def edit_services():
    while True:
        # Print the list of choices
        print()
        print('=' * 27)
        print('Admin Editing service menu:')
        print('=' * 27)
        print_services()
        print()
        print('1. Remove service')
        print('2. Add service')
        print('3. Modify service')
        print()

        # Asks for input and checks
        user_input = input('Enter your choice of action (ENTER to exit): ').strip()

        if (user_input in '123') and (len(user_input) <= 1):   
            # Validation for input
            if user_input == '1':
                remove_service()         
            elif user_input == '2':
                add_service()
            elif user_input == '3':
                modify_service()
            else:
                break
        else:
            print(Fore.RED + 'You have entered an invalid input, enter an index in the range from 1-3')
            time.sleep(1.5)


# Function to print the services
def print_services():
    print()
    # Prints the list of services
    print('The list of services currently available:')
    for i, (service, price) in enumerate(services.items()):
        print(f'{i + 1}. {service:20} : \t${price}k/year')


# Function to remove services
def remove_service():
    # If the services dictionary is not empty, allow admin to remove services
    while services:
        # Print the list of services
        print_services()
        
        # Asks for what the admin would like to remove
        user_input = input('Enter the service index/name you would like to remove (ENTER to exit): ').strip()

        # Removing service
        if (user_input.isnumeric()) and (0 < int(user_input) <= len(services)):
            print(Fore.GREEN + f'{list(services.keys())[int(user_input) - 1]} has been removed from the services')
            time.sleep(1.5)
            # Find service to be deleted
            service_delete = list(services.keys())[int(user_input) - 1]
            # Checks every user for the service and deletes it (including cart)
            for user in users:
                if users[user]['cart']:
                    for item in users[user]['cart']:
                        if item == service_delete:
                            users[user]['cart'].remove(item)

                if len(users[user].keys()) > 4:
                    # Creates a list of keys to be deleted
                    to_be_deleted = []
                    for i in range(4, len(users[user].keys())):
                        if service_delete in users[user][list(users[user].keys())[i]]:
                            # If found service delete it
                            users[user][list(users[user].keys())[i]].remove(service_delete)
                            # If user no longer has any subscriptions after removing the service delete the entire key
                            if not users[user][list(users[user].keys())[i]]:
                                to_be_deleted.append(list(users[user].keys())[i])

                    for date in to_be_deleted:
                        del(users[user][date])

            # Deletes service from the service.json file
            del(services[service_delete]) 

        # Invalid input
        elif user_input:
            print(Fore.RED + f'You have entered an invalid input, enter an index from the range of 1-{len(services)}')
            time.sleep(1.5)
        # ENTER to exit
        else:
            break
    else:
        print(Fore.RED + 'There are no services currently')
        time.sleep(1.5)


# Function to add service
def add_service():
    while True:
        # Prints the list of services
        print_services()

        # Asks for the name of the new service and checks if it exists
        new_service = input('Enter the service name you wish to add, limit to 20 characters (ENTER to exit): ').strip()

        # Validation for input
        if (new_service.upper() not in [service.upper() for service in list(services.keys())]):
            if (len(new_service) <= 20):
                # Asks for the price of the new service
                if new_service:
                    while True:
                        new_service_price = input('Input the price of the service ($k/yr) and less than 1000k: ')
                        # Validation for input
                        try:
                            if float(new_service_price) <= 1000:
                                break
                            else:
                                print(Fore.RED + 'The price exceeds 1000k')
                                time.sleep(1.5)
                        except ValueError:
                            print(Fore.RED + 'You have entered a invalid input')
                            time.sleep(1.5)
                            continue
                    # Adds new service 
                    new_service_price = round((float(new_service_price)), 1)
                    print(Fore.GREEN + f'{new_service} with the price of ${new_service_price}k/yr has been added to the services')
                    time.sleep(1.5)
                    services[new_service] = new_service_price
                else:
                    break
            else:
                print(Fore.RED + 'You entered a service exceeding 20 characters')
                time.sleep(1.5)
        else:
            print(Fore.RED + 'The service already exists')
            time.sleep(1.5)


# Function to modify service
def modify_service():
    while True:
        # Loop for input
        while True:
            # Print the lists of services
            print_services()
            # Asks for what service to modify
            user_input = input('Enter the service index you would like to modify (ENTER to exit): ').strip()

            # Validation of input
            if (user_input.isnumeric()) and (0 < int(user_input) <= len(services)):
                key_modify = list(services.keys())[int(user_input) - 1]
                break
            elif user_input:
                print(Fore.RED + f'You have entered a service that does not exist, enter an index from 1-{len(services)}')
                time.sleep(1.5)
            else:
                break

        # ENTER to exit
        if not user_input:
            break
        
        # Checks if input is valid
        while True:
            # Print choices available
            print('\n1. To modify name of service')
            print('2. To modify the price of service\n')

            user_input = input('Input your choice of action or (ENTER to exit): ').strip()

            # Validation of input
            if (user_input in '12') and (len(user_input) <= 1):
                break
            print(Fore.RED + 'You have entered an invalid input, enter an index from 1-2')
            time.sleep(1.5)

        # Modify name of service
        if user_input == '1':
            while True:
                user_input = input('Enter the new name for the service, limit to 20 char (ENTER to exit): ').strip()

                # Validation of input
                if (user_input.upper() not in [service.upper() for service in list(services.keys())]):
                    if (len(user_input) <= 20):
                        break
                    else:
                        print(Fore.RED + 'You entered a service exceeding 20 characters')
                        time.sleep(1.5)
                else:
                    print(Fore.RED + 'The service already exists')
                    time.sleep(1.5)

            if user_input:
                print(Fore.GREEN + f'The name of {key_modify} has been changed to {user_input}')
                time.sleep(1.5)
                # Changes key name in services.json
                services[user_input] = services.pop(key_modify)
                # Checks if any users has the service and modifies the price
                for user in users:
                    if len(users[user].keys()) > 4:
                        for i in range(4, len(users[user].keys())):
                            if key_modify in users[user][list(users[user].keys())[i]]:
                                users[user][list(users[user].keys())[i]].remove(key_modify)
                                users[user][list(users[user].keys())[i]].append(user_input)
    
        # Modify price of service
        elif user_input == '2':
            while True:
                user_input = input('Input the new price of the service ($k/yr) and less than 1000k (ENTER to exit): ').strip()
                # Validation of input
                try:
                    if (len(user_input) == 0) or (float(user_input) < 1000):
                        break
                    else:
                        print(Fore.RED + 'The price exceeds 1000k')
                        time.sleep(1.5)
                except ValueError:
                    print(Fore.RED + 'You have entered a invalid input')
                    time.sleep(1.5)
                    continue
            if user_input:
                user_input = round((float(user_input)), 1)
                print(Fore.GREEN + f'The price of {key_modify} changed from {services[key_modify]} to {user_input}')
                time.sleep(1.5)
                # Modify the price in services.json
                services[key_modify] = user_input


# Runs the menu function
edit_services()

# Writing the new dictionary back to the file
services_file = open('C:.\\esp_data\\services.json', 'w')
services_file.write(json.dumps(services, indent=4))
services_file.close()
# Write new user data into file
users_file = open('C:.\\esp_data\\user.json', 'w')
users_file.write(json.dumps(users, indent=4))
users_file.close()