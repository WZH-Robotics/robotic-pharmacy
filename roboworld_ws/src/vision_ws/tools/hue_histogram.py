import pyrealsense2 as rs
import numpy as np
import cv2

# 전역 변수 설정
points = []  # 클릭한 점들을 저장할 리스트
mask = None  # 다각형 마스크
hsv_roi = None  # HSV 값 추출을 위한 ROI

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
                hsv_min = np.min(hsv_values, axis=0)
                hsv_max = np.max(hsv_values, axis=0)
                print(f"HSV 범위: Min: {hsv_min}, Max: {hsv_max}")

                # Hue 히스토그램 생성
                hue_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
                cv2.normalize(hue_hist, hue_hist, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

                # 히스토그램 그리기
                hist_img = np.zeros((200, 180, 3), dtype=np.uint8)
                for x in range(180):
                    cv2.line(hist_img, (x, 200), (x, 200 - int(hue_hist[x])), (255, 255, 255))

                # 히스토그램 출력
                cv2.imshow('Hue Histogram', hist_img)

# RealSense 카메라 설정
pipeline = rs.pipeline()
config = rs.config()

# 스트림 설정 (컬러 스트림)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 파이프라인 시작
pipeline.start(config)

cv2.namedWindow('RealSense Camera')
cv2.setMouseCallback('RealSense Camera', select_points)

try:
    while True:
        # 프레임 가져오기
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        
        if not color_frame:
            continue
        
        # 컬러 프레임을 numpy 배열로 변환
        frame = np.asanyarray(color_frame.get_data())
        frame = cv2.GaussianBlur(frame, (5, 5), 0) # 노, 빨, 하, 보 할때는 5x5였음

        frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=50)

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
        cv2.imshow('RealSense Camera', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # 파이프라인 중지
    pipeline.stop()
    cv2.destroyAllWindows()
