import socket
import threading
from socket_client import SocketClient

if __name__ == '__main__':
    server_list = [
        ('192.168.0.176', 20002),  # kiosk server
        #('127.0.0.1', 20002),  # controllor server
        #('127.0.0.1', 20002),  # arduino1 server
        #('127.0.0.1', 20002),  # arduino2 server
        # 추가 서버 목록
    ]
    
    threads = []
    
    for host, port in server_list:
        data = f"Message to {host}:{port}"
        server = SocketClient(host, port)
        thread = threading.Thread(target=server.communicate(data), args=(host, port))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
