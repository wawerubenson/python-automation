import paramiko

# Define your servers
servers = [
    {'hostname': '192.168.100.8', 'username': 'benson', 'password': 'kogi254'},
    {'hostname': '192.168.100.10', 'username': 'benson', 'password': 'kogi254'},
    {'hostname': '192.168.100.14', 'username': 'benson', 'password': 'kogi254'},
]


    # Function to run a command on a remote server and return the output
def run_ssh_command(server, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server['hostname'], username=server['username'], password=server['password'])
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        if error:
            return f"Error on {server['hostname']}: {error}"
        
        return output
    except Exception as e:
        return f"Error connecting to {server['hostname']}: {str(e)}"

# Function to get the hostname of the server
def get_hostname(server):
    command = 'hostname'
    return run_ssh_command(server, command).strip()

# Function to check if apache2 service is running
def check_apache_status(server):
    command = 'systemctl is-active apache2'
    output = run_ssh_command(server, command).strip()
    if output == 'active':
        return f"{server['hostname']} Apache2 service is running"
    else:
        return f"{server['hostname']} Apache2 service is not running"

# Function to format the df -h output for disk usage
def format_disk_output(hostname, output):
    lines = output.splitlines()
    for line in lines:
        if line.startswith('/'):  # Assuming we want the root filesystem
            parts = line.split()
            use_percent = parts[4]
            return f"{hostname} remaining storage is {100 - int(use_percent[:-1])}%"
    return f"{hostname}: Unable to determine storage information"

# Function to get RAM and Swap usage
def get_ram_swap_info(server):
    command = 'free -m'
    output = run_ssh_command(server, command).strip()
    lines = output.splitlines()
    mem_info = {}
    for line in lines:
        if line.startswith('Mem:'):
            parts = line.split()
            mem_info['total_memory'] = int(parts[1])
            mem_info['used_memory'] = int(parts[2])
            mem_info['free_memory'] = int(parts[3])
            mem_info['used_memory_percent'] = int((mem_info['used_memory'] / mem_info['total_memory']) * 100)
        elif line.startswith('Swap:'):
            parts = line.split()
            mem_info['total_swap'] = int(parts[1])
            mem_info['used_swap'] = int(parts[2])
            mem_info['free_swap'] = int(parts[3])
            mem_info['used_swap_percent'] = int((mem_info['used_swap'] / mem_info['total_swap']) * 100)
    return mem_info

# Commands to run
disk_command = 'df -h'

# Run the commands on all servers and print the output
for server in servers:
    hostname = get_hostname(server)
    
    # Check disk usage
    disk_output = run_ssh_command(server, disk_command)
    formatted_disk_output = format_disk_output(hostname, disk_output)
    print(formatted_disk_output)
    
    # Check Apache status
    apache_status = check_apache_status(server)
    print(apache_status)
    
    # Get RAM and Swap usage
    ram_swap_info = get_ram_swap_info(server)
    ram_output = (f"{hostname} total RAM: {ram_swap_info['total_memory']}MB, "
                  f"used RAM: {ram_swap_info['used_memory_percent']}%, "
                  f"total Swap: {ram_swap_info['total_swap']}MB, "
                  f"used Swap: {ram_swap_info['used_swap_percent']}%")
    print(ram_output)
    
    print("=" * 60)