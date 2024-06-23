import paramiko
from getpass import getpass

host = "192.168.100.8"
username = input("Enter username: ") or "benson"
password = getpass("enter password: ") or "kogi254"
sudo_password = "kogi254"

session = paramiko.SSHClient()
session.load_system_host_keys()
session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

session.load_system_host_keys()

session.connect(
    hostname=host,
    username=username,
    password=password
)

commands = [
    'ls /',
    'echo $USER',
    'hostname',
    'ip a',
    'echo {} | sudo -S apt update'.format(sudo_password)
]

for command in commands:
    print(f"{'#'*10} Executing the command: {command}{'#'*10}")
    stdin, stdout, stderr = session.exec_command(command)
    stdin.write(sudo_password + '\n')
    stdin.flush()
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(err)

session.close()
