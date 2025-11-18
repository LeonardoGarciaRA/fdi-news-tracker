#!/usr/bin/env python3
"""
Create a public tunnel for the Flask app using localhost.run
"""
import subprocess
import sys
import time

def create_tunnel():
    print("Creating public tunnel...")
    print("This will create a public URL for your Flask app.")
    print("Press Ctrl+C to stop the tunnel.\n")
    
    # Use SSH to create tunnel via localhost.run
    try:
        # localhost.run provides free SSH tunnels
        cmd = ['ssh', '-R', '80:localhost:5000', 'ssh.localhost.run']
        print("Connecting to localhost.run...")
        print("Your public URL will be displayed below:\n")
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nTunnel closed.")
    except FileNotFoundError:
        print("SSH not found. Trying alternative method...")
        # Alternative: use serveo.net
        try:
            cmd = ['ssh', '-R', '80:localhost:5000', 'serveo.net']
            subprocess.run(cmd)
        except:
            print("Could not create tunnel. Please install SSH or use a cloud hosting service.")
            sys.exit(1)

if __name__ == '__main__':
    create_tunnel()

