import socket
import threading
import queue
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import config

from vision_ws.color_detector import start_detection_with_input
from data_parser import parse_kiosk_data
from vision_ws.autopack import detect_pill_count

def handle_kiosk_connection(kiosk_socket, kiosk_queue):
    while True:
        try:
            # 키오스크에서 데이터를 받음
            data = kiosk_socket.recv(1024).decode()
            if data:
                print(f"Received from kiosk: {data}")
                parsed_data = parse_kiosk_data(data)
                kiosk_queue.put(parsed_data) # 데이터를 Queue에 저장하여 Controller로 보낼 준비
        except Exception as e:
            print(f"Kiosk connection error: {e}")
            break

def handle_controller_connection(controller_socket, kiosk_queue):
    ready = True
    while True:
        try:
            if ready:
                if not kiosk_queue.empty():
                    data = kiosk_queue.get()
                    # Controller에 데이터 전송
                    controller_socket.sendall(data.encode())
                    ready = False
                    print(f"Sent to controller: {data}")
                
            # Controller로부터 응답 받기
            # need to make response case
            # example
            # 1~8 -> check that dispensor 'num' is empty
            # 9 -> autopack is ready to check
            # 10 -> process done. ready to get data
            #rea3dy = False
                #data = "vit_c:101,vit_h:101,jelly:020"
                #controller_socket.sendall(data.encode())
                #ready = False
                #print(f"Sent to controller: {data}")

            else: # ready = False
                response = int(controller_socket.recv(1024).decode())
                print(f"Received from controller: {response}")

                if 0<response<9:  # refill empty dispensor
                    # 응답에 따라 x, z 거리 계산
                    x,z = start_detection_with_input(response) # 예시 데이터
                    #x,z = 123,456
                    print(f"Calculated x: {x}, z: {z}")
                    
                    position_data = f"{x},{z}"
                    print(f"Send position to controller: {position_data}")
                    controller_socket.sendall(position_data.encode())

                    time.sleep(10)

                if response==9: # check autopack medicine state
                    medi_cam_value = detect_pill_count()
                    controller_socket.sendall(medi_cam_value.encode())

                if response=='0':
                    ready = True
                else:
                    print("none process is set")
                    continue

        except Exception as e:
            print(f"Controller connection error: {e}")
            break

def start_kiosk_client(kiosk_ip, kiosk_port, kiosk_queue):
    kiosk_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #while not kiosk_socket.connect:
    kiosk_socket.connect((kiosk_ip, kiosk_port))
    handle_kiosk_connection(kiosk_socket, kiosk_queue)

def start_controller_client(controller_ip, controller_port, kiosk_queue):
    controller_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #while not controller_socket.connect:
    controller_socket.connect((controller_ip, controller_port))
    handle_controller_connection(controller_socket, kiosk_queue)

if __name__ == "__main__":

    kiosk_ip = config.KIOSK_IP
    kiosk_port = config.KIOSK_PORT
    controller_ip = config.CONTROLLER_IP
    controller_port = config.CONTROLLER_PORT

    # Queue를 사용하여 키오스크와 컨트롤러 간 데이터 전달
    kiosk_queue = queue.Queue()
    sample_data = "vit_s:101,vit_m:111"#,jelly:020,mint_k:010"
    #sample_data = "4:4,'스완슨 비타민': 'vit_s','커클랜드 비타민': 'vit_c','호바흐 비타민': 'vit_h','메가씨 비타민': 'vit_m','민티아 칼피스': 'mint_k','민티아 콜드 스매쉬': 'mint_c','민티아 포도': 'mint_g','젤리빈': 'jelly'"
    kiosk_queue.put(sample_data)

    # 키오스크와 Controller 통신을 각각 스레드로 실행
    #kiosk_thread = threading.Thread(target=start_kiosk_client, args=(kiosk_ip, kiosk_port, kiosk_queue))
    controller_thread = threading.Thread(target=start_controller_client, args=(controller_ip, controller_port, kiosk_queue))

    #kiosk_thread.start()
    controller_thread.start()

    #kiosk_thread.join()
    controller_thread.join()
