import paramiko
from getpass import getpass

# List of IP addresses
hosts = ["192.168.100.10", "192.168.100.8", "192.168.100.14"]

# Function to connect to a host and execute commands
def check_disk_space(host, username, password, sudo_password):
    session = paramiko.SSHClient()
    session.load_system_host_keys()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        session.connect(hostname=host, username=username, password=password)
        
        commands = [
            'hostname',
            'df -h / | tail -1 | awk \'{print $5}\''
        ]
        
        results = {}
        for command in commands:
            stdin, stdout, stderr = session.exec_command(command)
            if 'sudo' in command:
                stdin.write(sudo_password + '\n')
                stdin.flush()
            results[command] = stdout.read().decode().strip()
            stderr_output = stderr.read().decode().strip()
            if stderr_output:
                results[command] += f" (stderr: {stderr_output})"

        hostname = results['hostname']
        disk_usage = results['df -h / | tail -1 | awk \'{print $5}\'']

        print(f"{hostname} remaining storage: {disk_usage}")
    
    except Exception as e:
        print(f"Failed to connect to {host}: {e}")
    
    finally:
        session.close()

# Get user credentials
username = input("Enter username: ") or "benson"
password = getpass("Enter password: ") or "kogi254"
sudo_password = "kogi254"  # Use the same password for sudo or prompt for a different one if needed

# Run the check on each host
for host in hosts:
    check_disk_space(host, username, password, sudo_password)
