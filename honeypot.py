#LIBRARIES
import argparse
from ssh_honeypot import *
from web_honeypot import *

#PARSE ARGUMENTS

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--address', type=str, required=True)
    parser.add_argument('-p', '--port', type=int, required=True)
    parser.add_argument('-u', '--username', type=str)
    parser.add_argument('-pw', '--password', type=str)

    parser.add_argument('-s', '--ssh', action="store_true")
    parser.add_argument('-w', '--http', action="store_true")

    args = parser.parse_args()

    if not args.username:
        args.username='admin'
    if not args.password:
        args.password='admin'

    try:
        if args.ssh:
            print(f"[~] Running SSH Honeypot on {args.address}:{args.port} | Username: {args.username} | Password: {args.password}")
            honeypot(args.address, args.port, args.username, args.password)

        elif args.http:
            print(f"[~] Running HTTP Honeypot on {args.address}:{args.port} | Username: {args.username} | Password: {args.password}")
            run_web_honeypot(args.port, args.username, args.password)
        else:
            print("[!] Choose a honeypot type (SSH --ssh) or (HTTP --http)")

    except Exception as e:
        print(f"\n[!] Error: {e}")
        print("\n Exiting HONEYPY....\n")

