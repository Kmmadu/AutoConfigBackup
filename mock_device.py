#!/usr/bin/env python3
"""Mock Cisco device for testing - responds with fake config"""

import socket
import threading
import time

def handle_client(conn):
    """Handle SSH-like connection (simplified for testing)"""
    try:
        # Send fake prompt
        conn.send(b"\r\nrouter> ")
        
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            cmd = data.decode().strip()
            
            if "show running-config" in cmd:
                # Send fake config
                config = """!
version 15.1
service timestamps debug datetime msec
service timestamps log datetime msec
hostname Test-Router
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
!
end"""
                conn.send(config.encode())
                conn.send(b"\r\nrouter> ")
            elif "enable" in cmd:
                conn.send(b"\r\nrouter# ")
            else:
                conn.send(b"\r\nrouter> ")
    except:
        pass
    finally:
        conn.close()

def start_mock_device(port=2222):
    """Start mock SSH server on localhost"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    server.listen(5)
    print(f"Mock Cisco device listening on port {port}")
    
    while True:
        conn, addr = server.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    start_mock_device()
