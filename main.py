import os
import subprocess
import time
from datetime import datetime
import sys
import configparser

def setup_logging(config):
    log_dir = config.get('Logging', 'log_dir', fallback='C:/logs')
    max_log_files = config.getint('Logging', 'max_log_files', fallback=10)

    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"Failed to create log directory: {e}")
            return None

    manage_log_files(log_dir, max_log_files)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"share_management_{timestamp}.log")
    return open(log_file, "w")

def manage_log_files(log_dir, max_log_files):
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    
    while len(log_files) >= max_log_files:
        oldest_file = min(log_files, key=lambda f: os.path.getctime(os.path.join(log_dir, f)))
        os.remove(os.path.join(log_dir, oldest_file))
        log_files.remove(oldest_file)

def log_message(file, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(message)
    if file:
        file.write(log_entry)
        file.flush()

def clear_share_sessions(log_file, config):
    try:
        exclude_users = config.get('ShareCleaning', 'exclude_users', fallback='').split(',')
        exclude_users = [user.strip().lower() for user in exclude_users]

        result = subprocess.run(['net', 'session'], capture_output=True, text=True)
        
        if "There are no entries in the list." in result.stdout:
            log_message(log_file, "No active share sessions found.")
            return

        sessions = result.stdout.split('\n')
        for session in sessions:
            if session.strip().startswith('\\\\'):
                parts = session.split()
                if len(parts) >= 2:
                    computer = parts[0]
                    user = parts[1].lower()
                    if user not in exclude_users:
                        try:
                            subprocess.run(['net', 'session', computer, '/delete'], check=True)
                            log_message(log_file, f"Cleared session for {computer} - {user}")
                        except subprocess.CalledProcessError as e:
                            log_message(log_file, f"Error clearing session for {computer} - {user}: {e}")
                    else:
                        log_message(log_file, f"Skipped session for excluded user: {user}")

        log_message(log_file, "Share session clearing process completed.")
    
    except subprocess.CalledProcessError as e:
        log_message(log_file, f"Error occurred while processing sessions: {e}")
    except Exception as e:
        log_message(log_file, f"An unexpected error occurred: {e}")

def disconnect_no_access_files(log_file, config):
    try:
        exclude_users = config.get('OpenFilesCleaning', 'exclude_users', fallback='').split(',')
        exclude_users = [user.strip().lower() for user in exclude_users]

        # Enable OpenFiles functionality
        subprocess.run(['openfiles', '/local', 'on'], check=True, capture_output=True)
        
        # Get list of open files
        result = subprocess.run(['openfiles', '/query', '/fo', 'csv'], capture_output=True, text=True, check=True)
        
        lines = result.stdout.split('\n')
        for line in lines[1:]:  # Skip header line
            parts = line.strip().split(',')
            if len(parts) >= 4:
                user = parts[1].strip('"').lower()
                access_mode = parts[3].strip('"')
                file_id = parts[0].strip('"')
                
                if access_mode == "No Access" and user not in exclude_users:
                    try:
                        subprocess.run(['openfiles', '/disconnect', '/id', file_id], check=True, capture_output=True)
                        log_message(log_file, f"Disconnected file with ID {file_id} for user {user}")
                    except subprocess.CalledProcessError as e:
                        log_message(log_file, f"Error disconnecting file with ID {file_id} for user {user}: {e}")
                else:
                    if user in exclude_users:
                        log_message(log_file, f"Skipped file with ID {file_id} for excluded user: {user}")
                    elif access_mode != "No Access":
                        log_message(log_file, f"Skipped file with ID {file_id} for user {user} (Access mode: {access_mode})")

        log_message(log_file, "Open files disconnection process completed.")
    
    except subprocess.CalledProcessError as e:
        log_message(log_file, f"Error occurred while processing open files: {e}")
    except Exception as e:
        log_message(log_file, f"An unexpected error occurred: {e}")

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists('settings.ini'):
        config.read('settings.ini')
    else:
        config['General'] = {'function': '1'}
        config['Logging'] = {'log_dir': 'C:/logs', 'max_log_files': '10'}
        config['ShareCleaning'] = {'exclude_users': 'administrator,fax'}
        config['OpenFilesCleaning'] = {'exclude_users': 'administrator,fax'}
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
    return config

def main():
    config = load_config()
    log_file = setup_logging(config)
    
    if os.name == 'nt' and not os.environ.get("ADMIN"):
        import ctypes
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            log_message(log_file, "This program requires administrator privileges to run.")
            log_message(log_file, "Please run this program as an administrator.")
            time.sleep(5)
            if log_file:
                log_file.close()
            sys.exit(1)

    try:
        function = config.getint('General', 'function', fallback=1)
        
        if function == 1:
            clear_share_sessions(log_file, config)
        elif function == 2:
            disconnect_no_access_files(log_file, config)
        else:
            log_message(log_file, f"Unknown function number: {function}")
    
    except Exception as e:
        log_message(log_file, f"An unexpected error occurred during program execution: {e}")
    finally:
        log_message(log_file, "Program execution completed. This window will close in 5 seconds...")
        time.sleep(5)
        if log_file:
            log_file.close()

if __name__ == "__main__":
    main()