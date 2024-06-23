import paramiko
from getpass import getpass
import slack
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize Slack client
slack_client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

def format_disk_output(hostname, output):
    lines = output.splitlines()
    for line in lines:
        if line.startswith('/'):  # Assuming we want the root filesystem
            parts = line.split()
            use_percent = parts[4]
            remaining_percent = 100 - int(use_percent[:-1])
            return f"{hostname} remaining storage is {remaining_percent}%"
    return f"{hostname}: Unable to determine storage information"

def check_pbx_storage(session):
    command = 'df -h /'
    stdin, stdout, stderr = session.exec_command(command)
    output = stdout.read().decode().strip()
    return format_disk_output(session.get_transport().getpeername()[0], output)

def send_slack_notification(message, channel='#test'):
    #print(message)  # Print message to terminal
    response = slack_client.chat_postMessage(channel=channel, text=message)
    return response['ok']

def main():
    hosts = ["192.168.100.8", "192.168.100.10", "192.168.100.14"]
    username = input("Enter username: ") or "benson"
    password = getpass("Enter password: ") or "kogi254"

    messages = []
    
    for host in hosts:
        session = paramiko.SSHClient()
        session.load_system_host_keys()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            session.connect(hostname=host, username=username, password=password)
            storage_info = check_pbx_storage(session)
            messages.append(storage_info)
            # Print storage info to terminal
            print(storage_info)
        
        except Exception as e:
            print(f"Failed to connect to {host}: {e}")
        
        finally:
            session.close()
    
    # Send Slack notification with all messages
    slack_message = f"Good morning <!channel> Below is today morning checkup:\n"
    slack_message += "\n".join(messages)
    
    success = send_slack_notification(slack_message)
    if success:
        print("\nSlack notification sent successfully.")
    else:
        print("\nFailed to send Slack notification.")

if __name__ == "__main__":
    main()
