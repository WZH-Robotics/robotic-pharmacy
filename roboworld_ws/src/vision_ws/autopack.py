import cv2
import numpy as np
import pyrealsense2 as rs
import time

# 알약 면적 기준에 따라 알약 개수 판단하는 함수
def determine_pill_count(area, contours):
    if len(contours) >= 2:  # 윤곽선이 두 개 이상일 때는 알약이 여러 개라고 판단
        return len(contours)  # 윤곽선 개수를 그대로 반환
    elif 2000 <= area <= 4000:  # 면적이 2000에서 4000 사이일 때는 두 개의 알약이 있다고 가정
        return 2
    elif area < 2000:  # 면적이 작을 경우 하나의 알약으로 판단
        return 1
    else:
        return 0  # 예외적인 경우는 알약이 없다고 판단

# 워터셰드 알고리즘을 적용하여 이미지 분할 및 윤곽선 추출
def apply_watershed(image, binary_mask):
    dist_transform = cv2.distanceTransform(binary_mask, cv2.DIST_L2, 5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.8 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(binary_mask, sure_fg)
    
    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1  # 배경을 1로 설정
    markers[unknown == 255] = 0  # 미지의 영역을 0으로 설정
    
    markers = cv2.watershed(image, markers)
    image[markers == -1] = [0, 0, 255]  # 경계선을 빨간색으로 표시
    
    return markers

# 3초 동안 카메라 프레임을 보고, 알약 개수 판정 후 값을 반환하는 함수
def detect_pill_count():
    pipeline = rs.pipeline()  # 리얼센스 파이프라인 설정
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)

    start_time = time.time()  # 시작 시간 저장
    pill_count1, pill_count2 = 0, 0  # 알약 개수 초기화

    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()

            if not color_frame:
                continue

            frame = np.asanyarray(color_frame.get_data())  # 프레임을 numpy 배열로 변환

            # 관심영역(ROI) 설정
            roi1 = frame[44:213, 108:290]  # 첫 번째 ROI
            roi2 = frame[52:218, 511:648]  # 두 번째 ROI

            # 그레이스케일 변환
            gray1 = cv2.cvtColor(roi1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY)

            # Otsu 이진화 적용
            ret1, otsu_binary1 = cv2.threshold(gray1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            ret2, otsu_binary2 = cv2.threshold(gray2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # 잡음 제거를 위한 침식 및 팽창
            kernel = np.ones((3, 3), np.uint8)
            erosion1 = cv2.erode(otsu_binary1, kernel, iterations=6)
            dilation1 = cv2.dilate(erosion1, kernel, iterations=3)
            erosion2 = cv2.erode(otsu_binary2, kernel, iterations=6)
            dilation2 = cv2.dilate(erosion2, kernel, iterations=3)

            # 워터셰드 알고리즘 적용
            markers1 = apply_watershed(roi1, dilation1)
            markers2 = apply_watershed(roi2, dilation2)

            # 윤곽선 추출
            contours1, _ = cv2.findContours(dilation1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours2, _ = cv2.findContours(dilation2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 윤곽선 면적 계산
            area1 = cv2.contourArea(contours1[0]) if len(contours1) > 0 else 0
            area2 = cv2.contourArea(contours2[0]) if len(contours2) > 0 else 0

            # 알약 개수 판단
            pill_count1 = determine_pill_count(area1, contours1)
            pill_count2 = determine_pill_count(area2, contours2)

            # 프레임에 ROI 박스와 윤곽선 표시
            cv2.rectangle(frame, (108, 44), (290, 213), (0, 255, 0), 2)
            cv2.rectangle(frame, (511, 52), (648, 218), (0, 255, 0), 2)
            cv2.imshow("RealSense Frame", frame)

            # 3초가 경과하면 루프 종료
            if time.time() - start_time >= 3:
                break

            # ESC를 누르면 루프 종료
            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        pipeline.stop()  # 파이프라인 종료
        cv2.destroyAllWindows()  # 모든 창 닫기

    # 세 자리 문자열로 변환하여 반환 (pill_count1 + 중간 0 + pill_count2)
    return f"{pill_count2}0{pill_count1}"

if __name__ == "__main__":
    # 알약 개수 감지 함수 호출 및 결과 출력
    result = detect_pill_count()
    print(f"Pill count result: {result}")
