import cv2
import numpy as np
import pyrealsense2 as rs
import time
from color_dict import colors

# 이전 프레임 좌표와 마지막 업데이트 시간을 저장할 딕셔너리
prev_contours = {}
no_movement_time = 1  # 0.05초 동안 움직임이 없으면 고정
movement_threshold = 10  # 좌표 변화 임계값 (5 -> 10으로 증가)

# 명암과 밝기 슬라이더 콜백 함수 (사용하지 않지만 필요함)
def nothing(x):
    pass

def detect_colors_with_realsense():
    # 리얼센스 파이프라인 설정
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    # 스트림 시작
    pipeline.start(config)

    # 윈도우와 트랙바 생성
    cv2.namedWindow('Color Detection')
    cv2.createTrackbar('Brightness', 'Color Detection', 50, 100, nothing)  # 밝기 조절 슬라이더
    cv2.createTrackbar('Contrast', 'Color Detection', 50, 100, nothing)    # 명암 조절 슬라이더

    try:
        while True:
            # 리얼센스 프레임 얻기
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()

            if not color_frame:
                continue

            # 프레임을 numpy 배열로 변환
            frame = np.asanyarray(color_frame.get_data())

            # 가우시안 블러 적용 (노이즈 제거)
            frame = cv2.GaussianBlur(frame, (5, 5), 0) # 노, 빨, 하, 보 할때는 5x5였음

            # 명암과 밝기 값 읽어오기
            brightness = cv2.getTrackbarPos('Brightness', 'Color Detection') - 50  # 트랙바 초기값이 50이므로 50을 뺌
            contrast = cv2.getTrackbarPos('Contrast', 'Color Detection') / 50.0    # 트랙바 범위를 0-100에서 0-2로 조정

            # 밝기 및 명암 조절
            frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)

            # HSV 색상 공간으로 변환
            hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


            # 색상별 HSV 범위 설정 및 박스 색, 영어 이름 설정
            colors = {
                'Green': ([70, 61, 76], [101, 116, 174], None, None, (0, 255, 0)),  # 초록색 박스 // 잘되긴하는데 뭔가 바운딩 박스가 지지직 거림 
                'Blue': ([107, 143, 87], [113, 255, 255], None, None, (255, 0, 0)), # 파란색 박스
                #'Blue': ([97, 100, 100], [115, 255, 255], None, None, (255, 0, 0)), # 파란색 박스 // 잘됐는데 왜 갑자기 안되지 
                # 'Rich Gold': ([7, 29, 84], [19, 207, 255], None, None, (255, 215, 0)), # 리치 골드 박스
                'Rich Gold': ([13, 64, 106], [30, 163, 255], None, None, (255, 215, 0)), # 리치 골드 박스
                #'Pink': ([149, 21, 189], [170, 170, 255], None, None, (255, 0, 255)),  # 핑크 박스 // 핑크는 잘 잡히는데 간간히 보라색도 잡음 왜지?
                'Red': ([0, 150, 100], [10, 255, 255], [170, 150, 100], [180, 255, 255], (0, 0, 255)),  # 다홍색 빨간 박스
                'Purple': ([115, 40, 43], [130, 168, 255], [131, 45, 43], [167, 171, 255], (255, 105, 180)), # 보라색 박스 // 잘되긴했음 
                #'Purple': ([109, 70, 57], [134, 166, 226], None, None, (255, 0, 255)),  # 보라색 범위 좁힘
                'Pink': ([150, 50, 180], [170, 204, 255], None, None, (255, 105, 180)),  # 핑크 박스 // 이거 보라랑 안 겹치게 됨 

                'Sky Blue': ([88, 112, 124], [101, 255, 255], None, None, (255, 255, 0)),  # 하늘색 박스 (S와 V 범위 조정)
                'Yellow': ([25, 100, 100], [35, 255, 255], None, None, (0, 255, 255))  # 노란색 박스
                

                }
            # 각 색상별 검출 처리
            for color_name, (lower1, upper1, lower2, upper2, box_color) in colors.items():
                # 색상에 따른 마스크 생성
                mask = cv2.inRange(hsv_image, np.array(lower1), np.array(upper1))
                if lower2 is not None and upper2 is not None:
                    mask += cv2.inRange(hsv_image, np.array(lower2), np.array(upper2))

                # 노이즈 제거를 위한 모폴로지 연산
                kernel = np.ones((7, 7), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

                # 컨투어 찾기
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    if cv2.contourArea(contour) > 1000:  # 너무 작은 컨투어는 무시
                        x, y, w, h = cv2.boundingRect(contour)
                        current_time = time.time()

                        # 이전 좌표가 없거나, 움직임이 있는지 확인
                        if color_name not in prev_contours or (abs(prev_contours[color_name][0] - x) > movement_threshold or abs(prev_contours[color_name][1] - y) > movement_threshold):
                            prev_contours[color_name] = (x, y, w, h, current_time)
                        else:
                            # 움직임이 없으면 마지막 시간 갱신
                            prev_contours[color_name] = (x, y, w, h, prev_contours[color_name][4])

                        # 0.05초 동안 움직임이 없으면 바운딩 박스를 고정
                        if current_time - prev_contours[color_name][4] > no_movement_time:
                            x_fixed, y_fixed, w_fixed, h_fixed = prev_contours[color_name][:4]
                            cv2.rectangle(frame, (x_fixed, y_fixed), (x_fixed + w_fixed, y_fixed + h_fixed), box_color, 2)
                            cv2.putText(frame, color_name, (x_fixed, y_fixed - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

            # 결과 이미지 출력
            cv2.imshow('Color Detection', hsv_image)

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

# 함수 실행
detect_colors_with_realsense()
