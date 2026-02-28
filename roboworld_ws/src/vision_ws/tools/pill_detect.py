import cv2
import numpy as np

# 카메라 스트림 열기
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

try:
    while True:
        # 실시간으로 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            print("프레임을 가져올 수 없습니다.")
            break

        # 이미지를 HSV로 변환
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 색상 범위 설정 (초록색, 푸른색, 노란색, 빨간색, 흰색)
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])

        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])

        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])

        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])

        lower_white = np.array([0, 0, 200])
        upper_white = np.array([255, 255, 255])

        # 각 색상에 대한 마스크 생성
        mask_green = cv2.inRange(hsv_image, lower_green, upper_green)
        mask_blue = cv2.inRange(hsv_image, lower_blue, upper_blue)
        mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
        mask_red1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        mask_white = cv2.inRange(hsv_image, lower_white, upper_white)

        # 빨간색은 두 개의 범위를 합쳐야 함
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)

        # 모든 마스크를 결합
        combined_mask = cv2.bitwise_or(mask_green, mask_blue)
        combined_mask = cv2.bitwise_or(combined_mask, mask_yellow)
        combined_mask = cv2.bitwise_or(combined_mask, mask_red)
        combined_mask = cv2.bitwise_or(combined_mask, mask_white)

        # 컨투어(윤곽선) 찾기
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 바운딩 박스 그리기
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 결과 이미지 출력
        cv2.imshow('Pill Detection for Multiple Colors', frame)
        cv2.imshow('Mask', combined_mask)  # 마스크 결과 확인

        # 'q' 키로 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()
