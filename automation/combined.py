import paramiko
from getpass import getpass
import requests
import csv
import datetime
import os

def check_pbx_storage(session):
    command = 'df -h / | tail -1 | awk \'{print $5}\''
    stdin, stdout, stderr = session.exec_command(command)
    storage_usage = stdout.read().decode().strip()
    return int(storage_usage.replace('%', ''))

def check_xivo_services(session):
    command = 'systemctl list-units --type=service | grep xivo'
    stdin, stdout, stderr = session.exec_command(command)
    services_status = stdout.read().decode().strip()
    return services_status

def check_calls(session):
    # Placeholder for actual call check logic
    incoming_calls_working = True
    outgoing_calls_working = True
    return incoming_calls_working, outgoing_calls_working

def check_hyper_backup(session):
    command = 'ps aux | grep HyperBackup | grep -v grep'
    stdin, stdout, stderr = session.exec_command(command)
    backup_running = bool(stdout.read().decode().strip())
    if backup_running:
        session.exec_command('systemctl stop HyperBackup')
    return backup_running

def send_slack_notification(message, webhook_url):
    payload = {'text': message}
    requests.post(webhook_url, json=payload)

def log_to_csv(data):
    filename = datetime.datetime.now().strftime("%Y-%m-checkups.csv")
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Date', 'Storage', 'Services', 'Calls', 'Backup'])
        writer.writerow(data)


def main():
    hosts = ["192.168.100.10", "192.168.100.11", "192.168.100.12"]
    username = input("Enter username: ") or "benson"
    password = getpass("Enter password: ") or "kogi254"
    sudo_password = password
    slack_webhook_url = 'YOUR_SLACK_WEBHOOK_URL'
    
    results = []
    
    for host in hosts:
        session = paramiko.SSHClient()
        session.load_system_host_keys()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            session.connect(hostname=host, username=username, password=password)
            
            storage = check_pbx_storage(session)
            services = check_xivo_services(session)
            incoming_calls, outgoing_calls = check_calls(session)
            backup_running = check_hyper_backup(session)
            
            # Notify if storage is above 40%
            if storage > 40:
                send_slack_notification(f"{host} storage usage is {storage}%", slack_webhook_url)
                
            # Report non-running xivo services
            if "running" not in services:
                send_slack_notification(f"{host} xivo services status: {services}", slack_webhook_url)
                
            # Report call issues
            if not incoming_calls or not outgoing_calls:
                send_slack_notification(f"{host} call issues detected. Incoming: {incoming_calls}, Outgoing: {outgoing_calls}", slack_webhook_url)
            
            # Log result
            result = [
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"{storage}%",
                services,
                f"Incoming: {incoming_calls}, Outgoing: {outgoing_calls}",
                "Paused" if backup_running else "Not running"
            ]
            results.append(result)
            
        except Exception as e:
            print(f"Failed to connect to {host}: {e}")
        
        finally:
            session.close()
    
    # Log to CSV
    for result in results:
        log_to_csv(result)
    
    # Send completion notification
    send_slack_notification("Morning checkup completed.", slack_webhook_url)

if __name__ == "__main__":
    main()
