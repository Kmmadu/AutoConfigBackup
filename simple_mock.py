#!/usr/bin/env python3
"""Simple mock Cisco device for testing"""

import socket
import threading
import sys

def handle_client(conn, addr):
    """Handle a single client connection"""
    print(f"Connection from {addr}")
    try:
        # Initial banner
        conn.send(b"\r\nMockRouter> ")
        
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            cmd = data.decode().strip().lower()
            print(f"Received: {cmd}")
            
            if "show running-config" in cmd or "show run" in cmd:
                config = """!
version 15.1
service timestamps debug datetime msec
service timestamps log datetime msec
!
hostname MockRouter
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.0
 no shutdown
!
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.255 area 0
!
end"""
                conn.send(config.encode())
                conn.send(b"\r\nMockRouter> ")
            elif "enable" in cmd:
                conn.send(b"\r\nMockRouter# ")
            elif "exit" in cmd or "quit" in cmd:
                conn.send(b"\r\nGoodbye\r\n")
                break
            else:
                conn.send(b"\r\n% Invalid command\r\nMockRouter> ")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        print(f"Connection closed from {addr}")

def start_mock_server(port=2222):
    """Start mock Cisco device server"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('127.0.0.1', port))
        server.listen(5)
        print(f"🎯 Mock Cisco device listening on 127.0.0.1:{port}")
        print(f"📝 Test with: ssh -p {port} admin@127.0.0.1")
        print("Press Ctrl+C to stop\n")
        
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down mock device...")
    except OSError as e:
        print(f"❌ Error: {e}")
        print(f"Port {port} might be in use. Try: fuser -k {port}/tcp")
    finally:
        server.close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 2222
    start_mock_server(port)
