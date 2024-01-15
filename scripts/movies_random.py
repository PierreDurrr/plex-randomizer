import os
import random
import shutil
import subprocess
import time
from rich.progress import Progress
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Get Plex login credentials from environment variables
plex_login = os.getenv("PLEX_LOGIN")
plex_password = os.getenv("PLEX_PASSWORD")

# User-defined variable for action (copy or symlink)
action_type = os.getenv("ACTION_TYPE", "copy")  # Default to "copy" if not specified

# User-defined variables for Plex server and library
plex_server_address = os.getenv("PLEX_SERVER_ADDRESS")
plex_server_port = os.getenv("PLEX_SERVER_PORT")
plex_library_section_id = int(os.getenv("PLEX_LIBRARY_SECTION_ID"))

# User-defined variables for source and destination folders
source_folder = os.getenv("SOURCE_FOLDER")
destination_folder = os.getenv("DESTINATION_FOLDER")

# User-defined variable for the amount of wanted movies
amount_of_wanted_movies = int(os.getenv("AMOUNT_OF_WANTED_MOVIES", 3))

# Check if PLEX_LOGIN and PLEX_PASSWORD are set
if not (plex_login and plex_password):
    print("PLEX_LOGIN and PLEX_PASSWORD must be set in the .env file.")
    exit(1)

print("\nRetrieving X-Plex-Token using Plex login/password...\n")

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
    print('Failed to retrieve X-Plex-Token.')
    exit(1)

print("############################################")
print(f'Your X_PLEX_TOKEN: {x_plex_token}')
print("############################################\n")

# Verify that the destination folder exists
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)
    print("Destination folder created successfully!\n")

# Get a list of all items in the destination folder
existing_items = os.listdir(destination_folder)

# Purge the contents of the destination folder (including symlinks.txt)
for item in existing_items:
    item_path = os.path.join(destination_folder, item)
    if os.path.isdir(item_path) and not os.path.islink(item_path):
        shutil.rmtree(item_path)
    elif os.path.isfile(item_path) or os.path.islink(item_path):
        os.remove(item_path)

print("Destination folder purged successfully!")

# Verify that the destination folder is empty
if not os.listdir(destination_folder):
    print("Destination folder is empty.\n")

    # Send an initial curl request to update Plex library
    curl_command_initial = [
        'curl',
        '-X', 'GET',
        f'{plex_server_address}:{plex_server_port}/library/sections/{plex_library_section_id}/refresh?X-Plex-Token={x_plex_token}'
    ]

    subprocess.run(curl_command_initial, check=True)
    print("Refresh plex for empty library!\n")

#    # Wait for 15 seconds
#    print("Waiting for 15 seconds...")
#    time.sleep(15)
#    print("\n")

    # Get a list of all subdirectories in the source folder
    subdirectories = [name for name in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, name))]

    # Choose random subdirectories based on the user-defined variable
    random_subdirectories = random.sample(subdirectories, amount_of_wanted_movies)

    # Print the picked-up subdirectories as bullet points
    print("Picked up subdirectories:")
    for i, subdirectory in enumerate(random_subdirectories, start=1):
        print(f"  - {i}. {subdirectory}")

    # Perform action based on user's choice (copy or symlink)
    symlink_paths = []
    with Progress() as progress:
        task = progress.add_task("[cyan]Performing action, please wait", total=len(random_subdirectories))
        
        for subdirectory in random_subdirectories:
            source_path = os.path.join(source_folder, subdirectory)
            destination_path = os.path.join(destination_folder, subdirectory)

            if action_type.lower() == "copy":
               # Perform copy using cp command
               subprocess.run(["cp", "-r", source_path, destination_path], check=True)
            elif action_type.lower() == "symlink":
                # Create a symbolic link
                os.symlink(source_path, destination_path)
                symlink_paths.append(destination_path)

            # Update the progress bar
            progress.update(task, advance=1)

    # Write symlink paths to a text file (if using symlinks)
    if action_type.lower() == "symlink":
        with open(os.path.join(destination_folder, 'symlinks.txt'), 'w') as f:
            f.write('\n'.join(symlink_paths))

    print(f"\nAction ({action_type}) performed successfully!\n")

    # Recursively scan linked directories to update Plex library
    subprocess.run(curl_command_initial, check=True)

    print("Plex library update triggered for linked directories.\n")

else:
    print("Destination folder is not empty. Aborting.")
