import pyrealsense2 as rs
import numpy as np
import cv2

# 전역 변수 설정
drawing = False  # 마우스 드래그 중인지 여부
ix, iy = -1, -1  # 박스 시작 좌표
fx, fy = -1, -1  # 박스 끝 좌표
hsv_roi = None  # HSV 값 추출을 위한 ROI

# 마우스 콜백 함수
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, fx, fy, drawing, hsv_roi
    
    if event == cv2.EVENT_LBUTTONDOWN:  # 마우스 왼쪽 버튼 누름
        drawing = True
        ix, iy = x, y
    
    elif event == cv2.EVENT_MOUSEMOVE:  # 마우스 움직일 때
        if drawing:
            fx, fy = x, y
    
    elif event == cv2.EVENT_LBUTTONUP:  # 마우스 왼쪽 버튼을 떼면
        drawing = False
        fx, fy = x, y
        hsv_roi = hsv_frame[iy:fy, ix:fx]  # 박스 내의 ROI 영역을 HSV로 저장
        if hsv_roi.size > 0:
            calculate_hsv_range(hsv_roi)

# HSV 범위 계산 함수
def calculate_hsv_range(hsv_roi):
    hue = hsv_roi[:, :, 0]  # hue 값만 추출
    sat = hsv_roi[:, :, 1]  # saturation 값만 추출
    val = hsv_roi[:, :, 2]  # value 값만 추출
    
    # hue 값을 0~180 범위로 나눠서 처리 (빨간색 구간이 두 부분으로 나뉘므로)
    low_hue = hue[hue < 90]  # 0 ~ 90 구간 (주로 낮은 hue 값)
    high_hue = hue[hue >= 90]  # 90 ~ 180 구간 (주로 높은 hue 값)

    if low_hue.size > 0 and high_hue.size > 0:  # 두 구간이 모두 있을 때
        # low_hue는 최소값, high_hue는 최대값을 사용
        hue_min = low_hue.max()
        hue_max = high_hue.min()
    else:
        # 한 구간만 존재할 때
        hue_min = hue.min()
        hue_max = hue.max()

    # Saturation과 Value는 일반적인 방법으로 계산
    sat_min = sat.min()
    sat_max = sat.max()
    val_min = val.min()
    val_max = val.max()

    print(f"HSV 범위: Min: [{hue_min}, {sat_min}, {val_min}], Max: [{hue_max}, {sat_max}, {val_max}]")

# RealSense 카메라 설정
pipeline = rs.pipeline()
config = rs.config()

# 스트림 설정 (컬러 스트림)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 파이프라인 시작
pipeline.start(config)

cv2.namedWindow('RealSense Camera')
cv2.setMouseCallback('RealSense Camera', draw_rectangle)

try:
    while True:
        # 프레임 가져오기
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        
        if not color_frame:
            continue
        
        # 컬러 프레임을 numpy 배열로 변환
        frame = np.asanyarray(color_frame.get_data())
        frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=50)
        # BGR을 HSV로 변환
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 드래그 중이면 박스를 그리기
        if ix != -1 and iy != -1 and fx != -1 and fy != -1:
            cv2.rectangle(frame, (ix, iy), (fx, fy), (0, 255, 0), 2)
        
        # 결과 이미지 출력
        cv2.imshow('RealSense Camera', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # 파이프라인 중지
    pipeline.stop()
    cv2.destroyAllWindows()
