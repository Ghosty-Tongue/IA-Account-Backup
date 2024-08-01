import asyncio
import os
import aiohttp
import xml.etree.ElementTree as ET
from tqdm import tqdm
from datetime import timedelta
from aiohttp import ClientSession
from tkinter import Tk, messagebox

def print_intro():
    intro_text = """
    Internet Archive Account Backup

    Welcome to the Internet Archive Account Backup tool! 
    This application allows you to back up the files associated 
    with an Internet Archive account. Just provide the username, 
    and we'll take care of the rest. Your files will be organized 
    into folders for each identifier, and we will show you how long 
    the backup will take.
    """
    print(intro_text)

def human_readable_size(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def calculate_estimated_time(total_size, speed_mbps):
    speed_bytes_per_sec = speed_mbps * 1024 * 1024
    estimated_seconds = total_size / speed_bytes_per_sec
    estimated_time = timedelta(seconds=estimated_seconds)
    
    weeks, remainder = divmod(estimated_seconds, 604800)
    days, remainder = divmod(remainder, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{int(weeks)} weeks, {int(days)} days, {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"

def show_message(title, message):
    root = Tk()
    root.withdraw() 
    messagebox.showinfo(title, message)
    root.destroy()

async def fetch_account_details(session, username, page):
    base_url = "https://archive.org/services/search/beta/page_production/"
    params = {
        'user_query': '',
        'page_type': 'account_details',
        'page_target': f'@{username.lower()}',
        'page_elements': '["uploads"]',
        'hits_per_page': 999,
        'page': page
    }
    try:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()
    except aiohttp.ClientError as e:
        print(f"Network error occurred while fetching account details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while fetching account details: {e}")
    return None

async def get_redirect_url(session, identifier):
    base_url = f"https://s3.us.archive.org/{identifier}/"
    try:
        async with session.get(base_url, allow_redirects=True) as response:
            if response.status == 200:
                return str(response.url)
            elif response.status == 403:
                content = await response.text()
                root = ET.fromstring(content)
                code = root.find('.//Code')
                if code is not None and code.text == 'NoSuchBucket':
                    print("Oops! That Identifier seems to have gone on vacation. It’s not here!")
                else:
                    print(f"Yikes! Something went wrong. Status code: {response.status}. Maybe try a different Identifier?")
            else:
                print(f"Uh-oh! Failed to retrieve the file list. Status code: {response.status}. It might be a wild goose chase!")
    except Exception as e:
        print(f"An error occurred while retrieving redirect URL: {e}")
    return None

async def list_files(session, redirect_url):
    try:
        async with session.get(redirect_url) as response:
            if response.status == 200:
                content = await response.text()
                root = ET.fromstring(content)
                files = []
                total_size = 0
                
                for content in root.findall('.//Contents'):
                    key = content.find('Key').text
                    size = int(content.find('Size').text)
                    files.append((key, size))
                    total_size += size
                
                return files, total_size
            else:
                print(f"Oopsie! Failed to retrieve the file list. Status code: {response.status}. The files are playing hide and seek!")
                return [], 0
    except Exception as e:
        print(f"An error occurred while listing files: {e}")
        return [], 0

async def download_file(session, redirect_url, file_name, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file_url = f"{redirect_url}/{file_name}"
    
    try:
        async with session.get(file_url) as response:
            if response.status == 200:
                total_size = int(response.headers.get('content-length', 0))
                with open(save_path, 'wb') as file, tqdm(
                    desc=file_name,
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    bar_format="{l_bar}{bar} [{elapsed}<{remaining}, {rate_fmt}]",
                ) as bar:
                    async for chunk in response.content.iter_any():
                        if chunk:
                            file.write(chunk)
                            bar.update(len(chunk))
                print(f"Success! '{file_name}' has been downloaded.")
            elif response.status == 403:
                print(f"Access denied to '{file_name}'. Status code: {response.status}.")
            else:
                print(f"Failed to download '{file_name}'. Status code: {response.status}.")
    except aiohttp.ClientError as e:
        print(f"Network error occurred while downloading '{file_name}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred while downloading '{file_name}': {e}")

async def process_identifier(session, identifier, save_folder):
    redirect_url = await get_redirect_url(session, identifier)
    if redirect_url:
        files, total_size = await list_files(session, redirect_url)
        identifier_folder = os.path.join(save_folder, identifier)
        os.makedirs(identifier_folder, exist_ok=True)
        print(f"Processing Identifier: {identifier}")
        for file_name, _ in files:
            save_path = os.path.join(identifier_folder, file_name.replace(' ', ''))
            await download_file(session, redirect_url, file_name, save_path)

async def main():
    print_intro()
    
    username = input("Enter the Internet Archive username: ").strip().lower()
    save_folder = os.path.join(os.getcwd(), username)
    os.makedirs(save_folder, exist_ok=True)

    async with ClientSession() as session:
        page = 1
        all_identifiers = []
        while True:
            try:
                account_details = await fetch_account_details(session, username, page)
                if account_details:
                    uploads = account_details['response']['body']['page_elements']['uploads']['hits']['hits']
                    if not uploads:
                        break
                    for item in uploads:
                        identifier = item['fields']['identifier']
                        all_identifiers.append(identifier)
                    page += 1
                    print(f"Page {page - 1} collected")
                else:
                    break
            except Exception as e:
                print(f"An error occurred while fetching data: {e}")
                break
        
        total_size = 0
        for identifier in all_identifiers:
            print(f"Processing Identifier: {identifier}")
            redirect_url = await get_redirect_url(session, identifier)
            if redirect_url:
                files, identifier_size = await list_files(session, redirect_url)
                print(f"Total size for Identifier '{identifier}': {human_readable_size(identifier_size)}")
                total_size += identifier_size
        
        print(f"\nTotal size for '{username}': {human_readable_size(total_size)}")
        estimated_time = calculate_estimated_time(total_size, speed_mbps=2.75)
        print(f"Estimated time to complete the backup: {estimated_time}")
        
        backup_confirmation = input("\nAre you ready to backup this user? (yes/no): ").strip().lower()
        if backup_confirmation == 'yes':
            for identifier in all_identifiers:
                print(f"\nStarting backup for Identifier: {identifier}")
                await process_identifier(session, identifier, save_folder)
            
            show_message("Backup Complete", "All identifiers have been successfully backed up!")
        else:
            show_message("Backup Cancelled", "The backup process has been cancelled.")

if __name__ == "__main__":
    asyncio.run(main())
