#test
import cv2
import numpy as np
import pyrealsense2 as rs
import time
import color_dict

# 이전 프레임 좌표와 마지막 업데이트 시간을 저장할 딕셔너리
prev_contours = {}
no_movement_time = 1  # 0.05초 동안 움직임이 없으면 고정
movement_threshold = 10  # 좌표 변화 임계값

# 배경 이미지 로드
background_image = cv2.imread('/home/w/roboworld_ws/src/vision_ws/background.png')

if background_image is None:
    print("Error: Could not load background image.")
    exit()

# 리얼센스 파이프라인 설정
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 스트림 시작
pipeline.start(config)

colors = color_dict.colors

# GrabCut에 사용할 마스크와 임시 변수 초기화
mask = np.zeros(background_image.shape[:2], np.uint8)
bgd_model = np.zeros((1, 65), np.float64)
fgd_model = np.zeros((1, 65), np.float64)

# 사각형을 이용해 전경과 배경을 분리할 대략적인 영역 설정
rect = (50, 50, background_image.shape[1] - 50, background_image.shape[0] - 50)

# GrabCut 실행 (초기 실행 시 5번의 반복)
cv2.grabCut(background_image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

# 마스크에서 전경 픽셀을 0 또는 1로 설정하여 전경 추출
mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
background_segmented = background_image * mask2[:, :, np.newaxis]

try:
    while True:
        # 리얼센스 프레임 얻기
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            continue

        # 현재 프레임을 numpy 배열로 변환
        frame = np.asanyarray(color_frame.get_data())

        # 배경 이미지와 현재 프레임 간 차이 계산
        diff_frame = cv2.absdiff(background_segmented, frame)

        # 가우시안 블러 적용 (노이즈 제거)
        frame = cv2.GaussianBlur(diff_frame, (5, 5), 0)

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
