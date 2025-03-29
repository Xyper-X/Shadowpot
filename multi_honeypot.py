import argparse
from ssh_honeypot import *
from web_honeypot import *
import multiprocessing

    

def run_ssh(address, port, username, password):
    print("[~] Running SSH Honeypot....")
    honeypot(address, port, username, password)

def run_http(port, username, password):
    print("[~] Running HTTP Honeypot....")
    run_web_honeypot(port, username, password)

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, default="0.0.0.0")
    parser.add_argument('-sp', '--ssh_port', type=int, default=2222)
    parser.add_argument('-wp', '--http_port', type=int, default=8000)
    parser.add_argument('-u', '--username', type=str, default="admin")
    parser.add_argument('-pw', '--password', type=str, default="admin")
    
    parser.add_argument('-b', '--both', action="store_true")  # New option to run both

    args = parser.parse_args()

    try:
        if args.both:
            # Run both honeypots in parallel
            ssh_process = multiprocessing.Process(target=run_ssh, args=(args.address, args.ssh_port, args.username, args.password))
            http_process = multiprocessing.Process(target=run_http, args=(args.http_port, args.username, args.password))
            
            ssh_process.start()
            http_process.start()
            
            ssh_process.join()
            http_process.join()
        else:
            print("[!] Choose a honeypot type: SSH (`--ssh`) or HTTP (`--http`) or Both (`--both`)")

    except KeyboardInterrupt:
        print("\n[!] Exiting Honeypot...")
