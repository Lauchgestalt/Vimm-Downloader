import os, json, re
from string import ascii_uppercase
import requests
from alive_progress import alive_bar
from bs4 import BeautifulSoup

# Config systems and filters
systems = ['GB', 'GBA', 'GBC']
filters = '&countries%5B%5D=11&translated=1&version=new&discs='

# Set necessary headers
headers = {
    'Referer': 'https://vimm.net/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4136.7 Safari/537.36 Edg/84.0.522.9'
}

# Colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Create categories array
characters = ['number'] + list(ascii_uppercase)
# Get already downloaded roms
with open('downloaded.json', 'r') as f:
    downloaded = json.loads(f.read())

# Loop through systems
for system in systems:
    print(f'\n{bcolors.HEADER}{bcolors.BOLD}Getting {system} roms\n{bcolors.ENDC}')

    # Create system folder + array key if not exists
    if not system in downloaded:
        downloaded[system] = []
    if not os.path.exists(f'./rom/{system}'):
        os.makedirs(f'./rom/{system}')

    # Loop through categories
    for char in characters:
        rom_links = []
        rom_ids = []
        url = f'https://vimm.net/vault/?p=list&action=filters&section={char}&system={system}{filters}'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')

        # Get all rom links in category
        roms = soup.find_all('a', {'href': re.compile(r'/vault/\d+')})
        for rom in roms:
            rom_links.append(rom['href'])
            
        for link in rom_links:
            r = requests.get(f'https://vimm.net{link}')
            soup = BeautifulSoup(r.content, 'html.parser')

            # Get all rom ids in found roms
            mediaId = soup.find('input', {'name': 'mediaId'})
            rom_ids.append(mediaId['value'])

        # If no roms found, skip category
        if len(rom_ids) == 0:
            print(f'{bcolors.HEADER}Getting {char} roms:{bcolors.ENDC} {bcolors.WARNING}No roms found matching your search criteria.{bcolors.ENDC}\n')
            continue
        print(f'{bcolors.HEADER}Getting {char} roms{bcolors.ENDC} {bcolors.OKGREEN}{len(rom_ids)} roms found{bcolors.ENDC}\n')

        for rom_id in rom_ids:
            try:
                with requests.get(f'https://download3.vimm.net/download/?mediaId={rom_id}', headers=headers, stream=True) as r:
                    r.raise_for_status()
                    filename = r.headers['Content-Disposition'].split('filename=')[1].replace('"', '')

                    # if file exists + not already downloaded, download
                    if r.status_code == 200 and not filename in downloaded[system]:
                        print(f'{bcolors.OKGREEN}Downloading {filename}')
                        file_size = int(r.headers['Content-Length'])
                        with alive_bar(file_size) as bar:
                            with open(f'./rom/{system}/{filename}', 'wb') as f:
                                for chunk in r.iter_content(chunk_size=1024 * 1024):
                                    size = f.write(chunk)
                                    bar(size)

                        # Add to downloaded.json when done
                        downloaded[system].append(filename)
                        with open('downloaded.json', 'w') as f:
                            f.write(json.dumps(downloaded))
                        print('\n')

                    elif filename in downloaded[system]:
                        print(f'{bcolors.OKGREEN}Already downloaded {filename}{bcolors.ENDC}\n')
            except:
                print(f'{bcolors.FAIL}Error downloading Game: {rom_id}. (Could be rate limited, try again later){bcolors.ENDC}\n')
