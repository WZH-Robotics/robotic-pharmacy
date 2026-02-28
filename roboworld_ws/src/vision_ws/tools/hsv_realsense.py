import pyrealsense2 as rs
import numpy as np
import cv2

# 전역 변수 설정
points = []  # 클릭한 점들을 저장할 리스트
mask = None  # 다각형 마스크
hsv_roi = None  # HSV 값 추출을 위한 ROI


# 명암과 밝기 슬라이더 콜백 함수 (사용하지 않지만 필요함)
def nothing(x):
    pass

# 마우스 콜백 함수
def select_points(event, x, y, flags, param):
    global points, mask, hsv_roi
    
    if event == cv2.EVENT_LBUTTONDOWN:  # 마우스 왼쪽 버튼을 누르면
        if len(points) < 4:
            points.append((x, y))  # 좌표를 리스트에 추가
            print(f"Point {len(points)}: ({x}, {y})")
        
        if len(points) == 4:  # 4개의 점이 모두 선택되면
            # 다각형 마스크 초기화
            mask = np.zeros_like(hsv_frame[:, :, 0], dtype=np.uint8)
            
            # 클릭한 4개의 점을 다각형으로 그리기
            pts = np.array(points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.fillPoly(mask, [pts], 255)
            
            # 마스크를 사용해 다각형 내부 영역의 HSV 값만 선택
            hsv_roi = cv2.bitwise_and(hsv_frame, hsv_frame, mask=mask)
            hsv_values = hsv_roi[mask == 255]
            
            if hsv_values.size > 0:
                # Hue 채널만 추출
                hue_channel = hsv_values[:, 0]
                
                # 중앙값 계산
                median_hue = np.median(hue_channel)
                
                # 허용 범위 설정 (중앙값 기준으로 +- 15도 허용)
                tolerance = 20
                hue_min = max(0, median_hue - tolerance)
                hue_max = min(179, median_hue + tolerance)  # HSV에서 Hue는 0-179 사이

                # Saturation과 Value도 마찬가지로 추출
                sat_values = hsv_values[:, 1]
                val_values = hsv_values[:, 2]
                sat_min, sat_max = np.min(sat_values), np.max(sat_values)
                val_min, val_max = np.min(val_values), np.max(val_values)
                
                print(f"HSV 범위: H: [{hue_min}, {hue_max}], S: [{sat_min}, {sat_max}], V: [{val_min}, {val_max}]")

# RealSense 카메라 설정
pipeline = rs.pipeline()
config = rs.config()

# 스트림 설정 (컬러 스트림)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 파이프라인 시작
pipeline.start(config)
    # 윈도우와 트랙바 생성
cv2.namedWindow('Color Detection')
cv2.createTrackbar('Brightness', 'Color Detection', 100, 100, nothing)  # 밝기 조절 슬라이더
cv2.createTrackbar('Contrast', 'Color Detection', 55, 100, nothing)    # 명암 조절 슬라이더

cv2.setMouseCallback('Color Detection', select_points)

try:
    while True:
        # 프레임 가져오기
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        
        if not color_frame:
            continue
        
        # 컬러 프레임을 numpy 배열로 변환
        frame = np.asanyarray(color_frame.get_data())
        frame = cv2.GaussianBlur(frame, (5, 5), 0)        
        # 명암과 밝기 값 읽어오기
        brightness = cv2.getTrackbarPos('Brightness', 'Color Detection') - 50  # 트랙바 초기값이 50이므로 50을 뺌
        contrast = cv2.getTrackbarPos('Contrast', 'Color Detection') / 50.0    # 트랙바 범위를 0-100에서 0-2로 조정

        # 밝기 및 명암 조절
        frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)
        
        # BGR을 HSV로 변환
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 사용자가 선택한 점을 그리기
        for point in points:
            cv2.circle(frame, point, 2, (0, 255, 0), -1)  # 선택한 좌표에 원 그리기
        
        # 4개의 점이 모두 선택된 후, 다각형 그리기
        if len(points) == 4:
            pts = np.array(points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=1)
        
        # 결과 이미지 출력
        cv2.imshow('Color Detection', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # 파이프라인 중지
    pipeline.stop()
    cv2.destroyAllWindows()
