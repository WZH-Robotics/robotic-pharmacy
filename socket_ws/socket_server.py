###################################################
########         This file is for          ########
########   controlling robot manipulator   ########
########  after receiving data from kiosk  ########
###################################################

import socket
import threading

# 소켓 서버 클래스 정의
class socket_server:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.clients = []  # 접속된 클라이언트 리스트
        
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            print(f'Server started at {self.host}:{self.port}')
        except Exception as e:
            print(f"Failed to bind to {self.host}:{self.port} - {e}")
    
    # 클라이언트와 통신을 처리하는 함수
    def handle_client(self, conn, addr):
        print(f'Connected by {addr}')
        self.clients.append(conn)  # 새로운 클라이언트를 리스트에 추가
        
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    continue
                
                decoded_data = data.decode()
                print(f"Received data from {addr}: {decoded_data}")
                
                if decoded_data.lower() == 'exit':
                    print(f"Exit command received from {addr}. Closing connection.")
                    break

                # 20002번 포트로부터 데이터 수신 시 모든 클라이언트에게 제어 신호 전송
                if self.port == 20002:
                    message = data_to_message(decoded_data)  # 데이터 -> 제어 신호로 변환
                    self.broadcast_to_clients(message)  # 연결된 모든 클라이언트에게 전송

                conn.sendall(f"Received: {decoded_data}".encode())
                print(f"Data '{decoded_data}' sent back to {addr}.")
            
            except ConnectionAbortedError:
                print(f"Client {addr} closed the connection.")
                break
            except Exception as e:
                print(f"Error receiving data from {addr}: {e}")
                break
            
        conn.close()
        self.clients.remove(conn)  # 클라이언트가 연결을 끊으면 리스트에서 제거
        print(f"Connection with {addr} closed.")
    
    # 모든 클라이언트에게 메시지를 전송하는 함수
    def broadcast_to_clients(self, message):
        for client in self.clients:
            try:
                client.sendall(message.encode())
                print(f"Sent message to client: {message}")
            except Exception as e:
                print(f"Failed to send message to a client: {e}")
                self.clients.remove(client)  # 전송 실패 시 클라이언트를 리스트에서 제거

    # 서버 시작 함수
    def start_server(self):
        print(f'Server is waiting for clients on port {self.port}...')
        while True:
            conn, addr = self.server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

# 데이터 -> 제어 신호로 변환하는 함수 (사용자 정의 로직에 맞게 수정)
def data_to_message(data):
    return f"Control signal for: {data}"