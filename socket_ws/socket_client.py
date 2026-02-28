###################################################
########         This file is for          ########
########   controlling robot manipulator   ########
########  after receiving data from kiosk  ########
###################################################

import socket
import time

class SocketClient:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.connect()  # 연결 시도
        
    def connect(self):
        while True:
            try:
                self.client.connect((self.host, self.port))
                print(f"Successfully connected to {self.host}:{self.port}")
                break  # 연결 성공 시 루프 종료
            except socket.error as e:
                print(f"Failed to connect to {self.host}:{self.port}. Error: {e}")
                time.sleep(1)  # 2초 대기 후 재시도
    
    def get_data(self):
        try:
            data = self.client.recv(1024).decode()
            print(f"Received from server {self.host}:{self.port}: {data}")
            return data
        except socket.error as e:
            print(f"Error receiving data: {e}")
            return None
    
    def send_data(self, data):
        try:
            self.client.send(data.encode())
        except socket.error as e:
            print(f"Error sending data: {e}")
    
    def close_connection(self):
        try:
            self.client.close()
            print(f"Connection to {self.host}:{self.port} closed.")
        except socket.error as e:
            print(f"Error closing the connection: {e}")
            
    def communicate(self, data_to_send):
        self.send_data(data_to_send)
        response = self.get_data()
        print(f"Response from {self.host}:{self.port} - {response}")
        #self.close_connection()

# Example usage:
# client = SocketClient("127.0.0.1", 20002)
# client.send_data("Hello Server")
# response = client.get_data()
# client.close_connection()
