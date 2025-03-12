import socket
import threading
import os
import pickle
import hashlib

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[INFO] Listening on {self.host}:{self.port}")

    def start(self):
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"[INFO] Accepted connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

    def handle_client(self, client_socket, addr):
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                message = pickle.loads(message)
                self.process_message(message, addr)
            except Exception as e:
                print(f"[ERROR] {e}")
                break
        client_socket.close()
        print(f"[INFO] Connection closed from {addr}")

    def process_message(self, message, addr):
        if message['type'] == 'PEER_LIST':
            self.update_peers(message['peers'])
            self.broadcast_peers()
        elif message['type'] == 'FILE_REQUEST':
            self.send_file(message['filename'], addr)

    def update_peers(self, new_peers):
        for peer in new_peers:
            self.peers[peer] = True
        print(f"[INFO] Peers updated: {self.peers}")

    def broadcast_peers(self):
        message = {
            'type': 'PEER_LIST',
            'peers': list(self.peers.keys())
        }
        for peer in self.peers:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(peer)
                sock.sendall(pickle.dumps(message))
                sock.close()
            except Exception as e:
                print(f"[ERROR] Failed to send peer list to {peer}: {e}")

    def send_file(self, filename, addr):
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                data = file.read()
            print(f"[INFO] Sending file {filename} to {addr}")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(addr)
                sock.sendall(data)
                sock.close()
            except Exception as e:
                print(f"[ERROR] Failed to send file to {addr}: {e}")
        else:
            print(f"[WARN] File {filename} not found")

    @staticmethod
    def calculate_file_hash(filename):
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

def run_peer(host='127.0.0.1', port=5000):
    peer = Peer(host, port)
    peer.start()

if __name__ == "__main__":
    run_peer()

# Client Code for testing
class PeerClient:
    def __init__(self, peer_address):
        self.peer_address = peer_address

    def request_file(self, filename):
        message = {
            'type': 'FILE_REQUEST',
            'filename': filename
        }
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.peer_address)
            sock.sendall(pickle.dumps(message))
            data = b''
            while True:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                data += chunk
            sock.close()
            with open(filename, 'wb') as file:
                file.write(data)
            print(f"[INFO] File {filename} downloaded successfully.")
        except Exception as e:
            print(f"[ERROR] Could not request file {filename}: {e}")

    def send_peer_list(self, peers):
        message = {
            'type': 'PEER_LIST',
            'peers': peers
        }
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.peer_address)
            sock.sendall(pickle.dumps(message))
            sock.close()
        except Exception as e:
            print(f"[ERROR] Could not send peer list: {e}")

if __name__ == '__main__':
    client = PeerClient(('127.0.0.1', 5000))
    client.request_file('sample.txt')

import sys

def start_application():
    if len(sys.argv) != 3:
        print("Usage: python peer_to_peer_network.py <host> <port>")
        return
    host = sys.argv[1]
    port = int(sys.argv[2])
    run_peer(host, port)

if __name__ == "__main__":
    start_application()