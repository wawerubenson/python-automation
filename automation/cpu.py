import paramiko

# Define your server
server = {'hostname': '192.168.100.14', 'username': 'benson', 'password': 'kogi254'}

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

# Function to get CPU details
def get_cpu_details(server):
    command = 'lscpu'
    return run_ssh_command(server, command)

# Function to get current CPU usage
def get_cpu_usage(server):
    command = 'mpstat'
    return run_ssh_command(server, command)

# Function to get CPU performance data for the last 5 days
def get_cpu_performance_last_5_days(server):
    command = 'sar -u -f /var/log/sa/sa$(date +%d -d "5 days ago")'
    return run_ssh_command(server, command)

# Get CPU details
cpu_details = get_cpu_details(server)
print(f"CPU Details for {server['hostname']}:\n{cpu_details}")

# Try to get current CPU usage
cpu_usage = get_cpu_usage(server)
if "Error" in cpu_usage:
    print(cpu_usage)
else:
    print(f"Current CPU Usage for {server['hostname']}:\n{cpu_usage}")

# Try to get CPU performance for the last 5 days
cpu_performance = get_cpu_performance_last_5_days(server)
if "Error" in cpu_performance:
    print(cpu_performance)
else:
    print(f"CPU Performance for the Last 5 Days for {server['hostname']}:\n{cpu_performance}")
