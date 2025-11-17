"""
Helper script to run Django server accessible on local network
"""
import subprocess
import socket
import sys
import os

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main():
    local_ip = get_local_ip()
    port = 8000
    
    print("=" * 60)
    print("Django Development Server - Network Access")
    print("=" * 60)
    print(f"\nYour local IP address: {local_ip}")
    print(f"\nTo access from another device on the same network:")
    print(f"  http://{local_ip}:{port}")
    print(f"\nTo access from this device:")
    print(f"  http://127.0.0.1:{port}")
    print("\n" + "=" * 60)
    print("Starting server... (Press Ctrl+C to stop)")
    print("=" * 60 + "\n")
    
    # Run Django server
    os.system(f"python manage.py runserver 0.0.0.0:{port}")

if __name__ == "__main__":
    main()

