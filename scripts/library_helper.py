import os
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET
from prettytable import PrettyTable

# Load environment variables from .env file
load_dotenv()

# Get Plex login credentials from environment variables
plex_login = os.getenv("PLEX_LOGIN")
plex_password = os.getenv("PLEX_PASSWORD")

# Get Plex server information from environment variables
plex_server_protocol = os.getenv("PLEX_SERVER_PROTOCOL")
plex_server_address = os.getenv("PLEX_SERVER_ADDRESS")
plex_server_port = os.getenv("PLEX_SERVER_PORT")

# Check if necessary environment variables are set
if not (plex_login and plex_password and plex_server_protocol and plex_server_address and plex_server_port):
    print("PLEX_LOGIN, PLEX_PASSWORD, PLEX_SERVER_PROTOCOL, PLEX_SERVER_ADDRESS, and PLEX_SERVER_PORT must be set in the .env file.")
    exit(1)

print("\n")
print('Retrieving a X-Plex-Token using Plex login/password...\n')

# Request the X-Plex-Token
response = requests.post(
    'https://plex.tv/users/sign_in.xml',
    auth=(plex_login, plex_password),
    headers={
        'X-Plex-Device-Name': 'PlexMediaServer',
        'X-Plex-Provides': 'server',
        'X-Plex-Version': '0.9',
        'X-Plex-Platform-Version': '0.9',
        'X-Plex-Platform': 'xcid',
        'X-Plex-Product': 'Plex Media Server',
        'X-Plex-Device': 'Linux',
        'X-Plex-Client-Identifier': 'XXXX',
    },
    params={'X-Plex-Token': ''}
)

# Extract X_PLEX_TOKEN from the response
x_plex_token = response.text.split('<authentication-token>')[1].split('</authentication-token>')[0]

if not x_plex_token:
    print(response.text)
    print('Failed to retrieve the X-Plex-Token.')
    exit(1)

print("############################################")
print(f'Your X_PLEX_TOKEN: {x_plex_token}')
print("############################################\n")

print("\n")
print('Retrieving current libraries/ID...\n')

# Use X_PLEX_TOKEN to get the list of libraries and their IDs
libraries_url = f'{plex_server_protocol}://{plex_server_address}:{plex_server_port}/library/sections?X-Plex-Token={x_plex_token}'
libraries_response = requests.get(libraries_url)

# Check if the response is XML (not JSON)
if 'xml' in libraries_response.headers.get('content-type', '').lower():
    libraries_data = ET.fromstring(libraries_response.text)
    libraries = libraries_data.findall('.//Directory')

    print(f'Your libraries/ID :\n')

    # Create a PrettyTable
    table = PrettyTable()
    table.field_names = ["Library Name", "Library ID"]

    for library in libraries:
        library_name = library.get('title')
        library_id = library.get('key')
        table.add_row([library_name, library_id])

    print(table)
    print(f'\n')
else:
    print('Failed to retrieve libraries information.')
    print(f'\n')
