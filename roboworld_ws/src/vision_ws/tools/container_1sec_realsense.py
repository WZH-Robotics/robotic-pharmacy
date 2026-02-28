import cv2
import numpy as np
import pyrealsense2 as rs
import time
from color_dict import colors

# 이전 프레임 좌표와 마지막 업데이트 시간을 저장할 딕셔너리
prev_contours = {}
no_movement_time = 1  # 0.05초 동안 움직임이 없으면 고정
movement_threshold = 10  # 좌표 변화 임계값 (5 -> 10으로 증가)

def detect_colors_with_realsense():
    # 리얼센스 파이프라인 설정
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    # 스트림 시작
    pipeline.start(config)
    
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
            frame = cv2.convertScaleAbs(frame, alpha = 1.1, beta = 50)
            
            # HSV 색상 공간으로 변환
            hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                        
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
            cv2.imshow('Color Detection', frame)

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

# 함수 실행
detect_colors_with_realsense()