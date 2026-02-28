import cv2
import numpy as np
import pyrealsense2 as rs
import time
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
import config

# 윤곽선 안정화를 위한 변수
prev_contours = {}  # 이전 프레임에서 검출된 윤곽선 정보 저장
stabilized_contours = {}  # 안정화된 윤곽선 정보 저장
stability_time = 1  # 윤곽선이 일정 시간 동안 안정된 후 고정할 시간 (초)
stability_threshold = 3  # 윤곽선의 각 좌표 변화 허용 범위 (픽셀)

# 고정된 좌표가 이미 출력되었는지 여부를 추적하는 변수
sent_contours = {}

# 카메라의 시리얼 번호
camera_serial_number1 = config.CAMERA_SERIAL_1  # 검수기 카메라
camera_serial_number2 = config.CAMERA_SERIAL_2  # 엔드이펙터 카메라

def initialize_camera(serial_number):
    # 리얼센스 파이프라인 설정
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device(serial_number)  # 카메라의 시리얼 번호로 장치 활성화
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)
    return pipeline

# x와 z 거리 계산 함수
def calculate_x_pos(x, y, w, h):
    x_center = 323.5907
    image_x1 = math.fabs(x - x_center)  # 이미지 중심
    image_x2 = math.fabs(image_x1 + w)  # right side of bounding box [pxl]

    image_height = h  # height of object in image [pxl]
    true_height = 115  # true height of object [mm]

    fx = 604.5513  # focal length in pixels (x-axis) [pxl/mm]
    fy = 604.5941  # focal length in pixels (y-axis)

    z = math.floor((fy * true_height) / image_height)  # depth of object [mm]

    sqr_f = fx * fx
    d1d2 = math.sqrt((sqr_f + image_x1 * image_x1) * (sqr_f + image_x2 * image_x2))
    mid_calc = sqr_f - image_x1 * image_x2

    x_distance = math.floor(z * 1.05 * math.sqrt((d1d2 - mid_calc) / (d1d2 + mid_calc)))

    if x + w < x_center:
        return -(x_distance - 50), z - 175
    elif x > x_center:
        return x_distance - 50, z - 175
    else:
        return 0, 0

# 윤곽선을 안정화하고 바운딩 박스와 색상 이름을 표시
def stabilize_contours(contour, color_name):
    global stabilized_contours, sent_contours
    x, y, w, h = cv2.boundingRect(contour)
    current_time = time.time()

    if color_name not in prev_contours:
        # 최초 검출 시 좌표 및 시간 저장
        prev_contours[color_name] = (x, y, w, h, current_time)
        sent_contours[color_name] = False  # 처음에 좌표가 출력되지 않음
    else:
        # x, y, w, h 좌표가 모두 stability_threshold 이상일 때만 업데이트
        prev_x, prev_y, prev_w, prev_h, prev_time = prev_contours[color_name]
        delta_x = abs(prev_x - x)
        delta_y = abs(prev_y - y)
        delta_w = abs(prev_w - w)
        delta_h = abs(prev_h - h)

        if delta_x > stability_threshold or delta_y > stability_threshold or delta_w > stability_threshold or delta_h > stability_threshold:
            # 좌표가 변화한 경우: 좌표와 시간을 갱신, 다시 출력 가능 상태로 변경
            prev_contours[color_name] = (x, y, w, h, current_time)
            sent_contours[color_name] = False  # 좌표가 움직였으므로 다시 출력 가능
        else:
            # 좌표 변화가 없으면 기존 시간을 유지
            prev_contours[color_name] = (x, y, w, h, prev_time)

    # 안정화 시간이 경과한 경우 좌표 고정
    if current_time - prev_contours[color_name][4] > stability_time:
        x_fixed, y_fixed, w_fixed, h_fixed = prev_contours[color_name][:4]

        if color_name not in stabilized_contours or \
                (x_fixed, y_fixed, w_fixed, h_fixed) != stabilized_contours[color_name]:
            stabilized_contours[color_name] = (x_fixed, y_fixed, w_fixed, h_fixed)

            # 좌표가 고정되고 아직 출력되지 않은 경우에만 좌표를 출력
            if not sent_contours[color_name]:
                x_pos, z_pos = calculate_x_pos(x_fixed, y_fixed, w_fixed, h_fixed)
                print(f"{color_name} detected at x: {x_pos}, z: {z_pos}")
                sent_contours[color_name] = True  # 좌표를 한 번 출력했으면 다시는 출력하지 않음
        return (x_fixed, y_fixed, w_fixed, h_fixed)
    return None

# Canny 엣지 검출 및 윤곽선 찾기
def apply_canny_and_find_contours(frame):
    blurred = cv2.GaussianBlur(frame, (9, 9), 0)
    edges = cv2.Canny(blurred, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, edges

# 마스크 정제 함수 (모폴로지 연산 사용)
def refine_mask(mask):
    kernel = np.ones((3, 3), np.uint8)
    refined_mask = cv2.erode(mask, kernel, iterations=2)
    refined_mask = cv2.dilate(refined_mask, kernel, iterations=2)
    return refined_mask

# 메인 함수: Otsu 이진화 및 Canny 엣지 검출 적용, 색상 검출 후 x, z 값을 반환
def apply_otsu_binarization_and_canny(color_input):
    pipeline = initialize_camera(camera_serial_number2)
    color_names = {"Orange", "Sky Blue", "Rich Gold", "Yellow", "Pink", "Dark Blue", "Green", "Red"}
    target_color = color_names[color_input-1]

    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            frame = np.asanyarray(color_frame.get_data())
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, otsu_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            kernel = np.ones((3, 3), np.uint8)
            erosion = cv2.erode(otsu_binary, kernel, iterations=6)
            dilation = cv2.dilate(erosion, kernel, iterations=3)
            contours, edges = apply_canny_and_find_contours(gray)
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            color_ranges = {
                "Orange": ([5, 150, 150], [15, 255, 255], (0, 165, 255)),
                "Sky Blue": ([90, 100, 100], [100, 255, 255], (255, 191, 0)),
                "Rich Gold": ([15, 139, 135], [20, 190, 172], (0, 215, 255)),
                "Yellow": ([26, 217, 177], [35, 255, 255], (0, 255, 255)),
                "Pink": ([160, 50, 150], [170, 255, 255], (255, 0, 255)),
                "Dark Blue": ([100, 150, 100], [130, 255, 255], (255, 191, 0)),
                "Green": ([73, 158, 112], [78, 234, 149], (0, 255, 0)),
                "Red": ([0, 205, 162], [5, 255, 255], (0, 0, 255)),
                "Purple": ([117, 44, 167], [131, 61, 189], (128, 0, 128)),
            }

            detected_colors = set()
            for contour in contours:
                if cv2.contourArea(contour) > 250:
                    for color_name, (lower, upper, contour_color) in color_ranges.items():
                        if color_name != target_color:  # 원하는 색상이 아니면 넘어감
                            continue

                        lower_bound = np.array(lower)
                        upper_bound = np.array(upper)
                        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
                        refined_mask = refine_mask(mask)
                        x, y, w, h = cv2.boundingRect(contour)
                        region = refined_mask[y:y + h, x:x + w]
                        if np.any(region):  # 원하는 색상이 검출된 경우
                            fixed_contour = stabilize_contours(contour, color_name)
                            if fixed_contour is not None:
                                x, y, w, h = fixed_contour
                                stabilized_contours[color_name] = (x, y, w, h)
                                # 원하는 색상이 검출되면 x, z 값 반환
                                x_pos, z_pos = calculate_x_pos(x, y, w, h)
                                return x_pos, z_pos  # 검출된 좌표 반환
            # 프레임 시각화
            cv2.imshow('Canny Edge Detection', edges)
            cv2.imshow('Color Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

# Dart Studio에서 입력된 색상에 따라 색상 검출 및 x, z 값 반환
def start_detection_with_input(color_input):
    x, z = apply_otsu_binarization_and_canny(color_input)
    if x is not None and z is not None:
        print(f"Detected {color_input} color at x: {x}, z: {z}")
        return x, z
    else:
        print(f"{color_input} 색상을 검출하지 못했습니다.")
        return None

if __name__ == "__main__":
    # 사용 예시:
    color_name = 'Orange'  # Dart Studio나 다른 곳에서 입력받은 색상
    x, z = start_detection_with_input(color_name)
    print(f"X = {x}, Z = {z}")