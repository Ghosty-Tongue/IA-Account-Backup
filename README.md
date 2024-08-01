# Internet Archive Account Backup

## Overview

The **Internet Archive Account Backup** tool is designed to help you back up files from an Internet Archive account. It fetches all the files associated with a specified username, organizes them by identifier, and downloads them to your local machine. The tool also provides an estimate of the total download time based on the size of the files and the expected download speed.

## Features

- **Fetches Account Details**: Retrieves all file identifiers associated with the provided username.
- **Estimates Download Time**: Calculates the estimated time to download all files based on file size and download speed.
- **Downloads Files**: Downloads each file one by one and saves them in organized folders.
- **Progress Tracking**: Displays a progress bar for each file download.
- **User Confirmation**: Asks for confirmation before starting the backup process.
- **Status Notifications**: Provides message boxes for successful and error backups.

## Requirements

- Python 3.7 or higher
- `aiohttp` for asynchronous HTTP requests
- `tqdm` for progress bars

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Ghosty-Tongue/internet-archive-account-backup.git
    ```

2. Navigate to the project directory:

    ```bash
    cd internet-archive-account-backup
    ```

3. Install the required packages:

    ```bash
    pip install aiohttp tqdm
    ```

## Usage

1. Run the script:

    ```bash
    python ia.py
    ```

2. Enter the Internet Archive username when prompted.

3. Review the estimated total size and download time for the backup.

4. Confirm if you are ready to start the backup.

5. The tool will download all files associated with the provided username into a folder named after the username.

## Example

```plaintext
Internet Archive Account Backup

Welcome to the Internet Archive Account Backup tool!
This application allows you to back up the files associated
with an Internet Archive account. Just provide the username,
and we'll take care of the rest. Your files will be organized
into folders for each identifier, and we will show you how long
the backup will take.

Enter the Internet Archive username: exampleuser

Processing Identifier: example_identifier
Total size for Identifier 'example_identifier': 10.00 GB
Total size for 'exampleuser': 10.00 GB
Estimated time to complete the backup: 1 days, 2 hours, 15 minutes, 30 seconds

Are you ready to backup this user? (yes/no): yes

Starting backup for Identifier: example_identifier
...
```

## Message Boxes

- **Backup Complete**: Indicates that the backup process has been successfully completed.
- **Backup Cancelled**: Indicates that the backup process was cancelled by the user.

## Contributing

If you have any suggestions or improvements, feel free to create a pull request or open an issue on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

For further assistance, please contact [Ghosty-Tongue](mailto:ghostytongue@example.com).
