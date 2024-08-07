import os
import subprocess
import time
from datetime import datetime
import sys

LOG_DIR = "C:/logs"
MAX_LOG_FILES = 10

def setup_logging():
    if not os.path.exists(LOG_DIR):
        try:
            os.makedirs(LOG_DIR)
        except Exception as e:
            print(f"Failed to create log directory: {e}")
            return None

    manage_log_files()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"share_session_clear_{timestamp}.log")
    return open(log_file, "w")

def manage_log_files():
    log_files = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]
    
    while len(log_files) >= MAX_LOG_FILES:
        oldest_file = min(log_files, key=lambda f: os.path.getctime(os.path.join(LOG_DIR, f)))
        os.remove(os.path.join(LOG_DIR, oldest_file))
        log_files.remove(oldest_file)

def log_message(file, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(message)
    if file:
        file.write(log_entry)
        file.flush()

def clear_share_sessions(log_file):
    try:
        result = subprocess.run(['net', 'session'], capture_output=True, text=True)
        
        if "There are no entries in the list." in result.stdout:
            log_message(log_file, "No active share sessions found.")
            return

        subprocess.run(['net', 'session', '/delete', '/y'], check=True)
        log_message(log_file, "All share sessions have been successfully cleared.")
    
    except subprocess.CalledProcessError as e:
        log_message(log_file, f"Error occurred while clearing sessions: {e}")
    except Exception as e:
        log_message(log_file, f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    log_file = setup_logging()
    
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
        clear_share_sessions(log_file)
    except Exception as e:
        log_message(log_file, f"An unexpected error occurred during program execution: {e}")
    finally:
        log_message(log_file, "Program execution completed. This window will close in 5 seconds...")
        time.sleep(5)
        if log_file:
            log_file.close()