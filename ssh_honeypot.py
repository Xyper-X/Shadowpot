#LIBRARY
import logging
from logging.handlers import RotatingFileHandler
import paramiko
import socket
import threading

#Constants
logging_format = logging.Formatter('%(message)s')
SSH_BANNER = 'SSH-2.0-OpenSSH_8.2p1 Debian-4ubuntu0'
host_key = paramiko.RSAKey(filename='server.key')

#Loggers
creds_logger=logging.getLogger('credslogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler('ssh_Failed.log',maxBytes=5000,backupCount=10)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)

ssh_logger=logging.getLogger('sshlogger')
ssh_logger.setLevel(logging.INFO)
ssh_handler = RotatingFileHandler('ssh_Success.log',maxBytes=5000,backupCount=10)
ssh_handler.setFormatter(logging_format)
ssh_logger.addHandler(ssh_handler)

session_logger=logging.getLogger('sessionlogger')
session_logger.setLevel(logging.INFO)
session_handler = RotatingFileHandler('ssh_session.log',maxBytes=5000,backupCount=10)
session_handler.setFormatter(logging_format)
session_logger.addHandler(session_handler)


#Shell_emulator
def emulated_shell(channel, client_ip):
    channel.send(b'\nroot-ubuntu4.0$ ')
    command = b''

    while True:
        char = channel.recv(1)
        if not char:
            break 

        channel.send(char)
        command += char

        if char == b'\r':
            command = command.strip()
            if command == b'exit':
                channel.send(b'\nGoodbye!\n')
                break
            elif command == b'pwd':
                response = b'\n/usr/local\r\n'
                session_logger.info(f"Command {command.decode()}" + " executed by : " + f"{client_ip}")
            elif command == b'whoami':
                response = b'\nroot\r\n'
                session_logger.info(f"Command {command.decode()}" + " executed by : " + f"{client_ip}")
            elif command == b'ls':
                response = b'\nDesktop\tDownloads\tPictures\tVideos\tImage\r\n'
                session_logger.info(f"Command {command.decode()}" + " executed by : " + f"{client_ip}")
            else:
                response = b'\n' + command + b'Command not found\r\n'
                session_logger.info(f"Command {command.decode()}" + " executed by : " + f"{client_ip}")

            channel.send(response)
            channel.send(b'\nroot-ubuntu4.0$ ')
            command = b''

    channel.close()














#ssh Server Socket

class Server(paramiko.ServerInterface):

    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username= input_username
        self.input_password= input_password

    def check_channel_request(self, kind: str, chanid: id) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        
    def get_auth(self):
        return "password"
    
    def check_auth_password(self, username, password):
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                ssh_logger.info(f" Successful SSH Login - Username: {username}, Password: {password} IP: {self.client_ip}")
                return paramiko.AUTH_SUCCESSFUL
            else:
                creds_logger.info(f" Failed SSH Login Attempt - Username: {username}, Password: {password}, IP: {self.client_ip}")
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True
    
    def check_channel_exec_request(self, channel, command):
        session_logger.info(f"Executed command: {command} from IP: {self.client_ip}")
        return True
    
def client_handle(client, addr, username, password):
        client_ip = addr[0]
        print(f"{client_ip} has connected to the server")

        try:
            transport = paramiko.Transport(client)
            transport.local_version = SSH_BANNER
            server = Server(client_ip=client_ip, input_username=username, input_password=password)

            transport.add_server_key(host_key)

            transport.start_server(server=server)

            channel = transport.accept(1024)
            if channel is None:
                print("No channel was Opened")
                return
            
            standard_banner = "Welcome to Ubuntu 22.04\r\n\r\n"
            channel.send(standard_banner)
            emulated_shell(channel,client_ip=client_ip)

        except Exception as error:
            print(error)
            print("!!! ERROR !!!")
            
        finally:
            try:
                transport.close()
            except Exception as error:
                print(error)
                print("!!! ERROR !!!")
        client.close()

#ssh based honeypot

def honeypot(address, port, username, password):
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))

    socks.listen(10)
    print(f"SSH server listening on port {port}")

    while True:
        try:
            client, addr = socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            ssh_honeypot_thread.start()
        except KeyboardInterrupt:
            print("\n[!] Stopping SSH Honeypot...")
            socks.close()
            break  
        except Exception as error:
            print(f"Error accepting connection: {error}")


#honeypot('127.0.0.1', 2222 , username=None, password=None) # Testing
