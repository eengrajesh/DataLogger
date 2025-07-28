import subprocess
import platform
import socket

def ping_host(host):
    """
    Pings a host to check for connectivity.
    """
    # Determine the ping command based on the operating system
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]

    try:
        # Execute the ping command
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def scan_ports(host, start_port, end_port):
    """
    Scans a range of ports on a host to find open ports.
    """
    open_ports = []
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

if __name__ == "__main__":
    pi_ip = input("Enter the IP address of the Raspberry Pi: ")
    if ping_host(pi_ip):
        print(f"Successfully connected to {pi_ip}")
        
        scan = input("Do you want to scan for open ports? (y/n): ")
        if scan.lower() == 'y':
            start = int(input("Enter the start port: "))
            end = int(input("Enter the end port: "))
            print(f"Scanning ports on {pi_ip}...")
            open_ports = scan_ports(pi_ip, start, end)
            if open_ports:
                print("Open ports are:")
                for port in open_ports:
                    print(port)
            else:
                print("No open ports found in the specified range.")
    else:
        print(f"Failed to connect to {pi_ip}")