# Auto Clear Folder Sessions

This Python script automatically clears Windows share folder sessions and logs the results. It's designed to run with administrator privileges and manage its own log files.

## Features

- Clears all active Windows share folder sessions
- Logs all actions and results
- Automatically manages log files, keeping only the 10 most recent logs
- Runs with a 5-second pause at the end for easy reading of results
- Requires administrator privileges to function correctly

## Requirements

- Windows operating system
- Python 3.x
- Administrator privileges

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yusyuan9224/Auto-Clear-Folder-Sessions.git
   ```
2. Navigate to the cloned directory:
   ```
   cd Auto-Clear-Folder-Sessions
   ```

## Usage

1. Right-click on the Python script and select "Run as administrator", or launch a command prompt as administrator and run:
   ```
   python clear_share_sessions.py
   ```
2. The script will automatically clear all active share sessions and log the results.
3. Logs are stored in `C:/logs/` with a timestamp in the filename.
4. The program will pause for 5 seconds before closing, allowing you to read the output.

## Log Management

- The script automatically manages log files in the `C:/logs/` directory.
- It keeps only the 10 most recent log files.
- Older log files are automatically deleted when this limit is exceeded.

## Caution

This script requires administrator privileges to function correctly. It will attempt to delete all active share sessions, so use it with care in production environments.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/yusyuan9224/Auto-Clear-Folder-Sessions/issues) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)