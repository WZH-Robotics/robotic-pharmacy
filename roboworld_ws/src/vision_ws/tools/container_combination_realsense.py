import cv2
import numpy as np
import pyrealsense2 as rs

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
            frame = cv2.GaussianBlur(frame, (9, 9), 0)

            # HSV 색상 공간으로 변환
            hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 색상별 HSV 범위 설정 및 박스 색, 영어 이름 설정
            colors = {
                'Red': ([0, 150, 100], [10, 255, 255], [170, 150, 100], [180, 255, 255], (0, 0, 255)),  # 다홍색 빨간 박스
                'Pink': ([167, 70, 160], [173, 204, 255], None, None, (255, 105, 180)),  # 핑크 박스
                'Green': ([35, 50, 50], [85, 255, 255], None, None, (0, 255, 0)),  # 초록색 박스
                'Teal': ([86, 50, 50], [98, 255, 255], None, None, (0, 128, 128)),  # 청록색 박스 (범위 조정)
                'Blue': ([115, 100, 70], [125, 255, 255], None, None, (255, 0, 0)),  # 파란색 박스
                'Purple': ([126, 70, 60], [160, 255, 255], None, None, (255, 0, 255)),  # 보라색 박스
                'Yellow': ([25, 100, 100], [35, 255, 255], None, None, (0, 255, 255)),  # 노란색 박스
                'Sky Blue': ([99, 100, 100], [110, 255, 255], None, None, (255, 255, 0)),  # 하늘색 박스 (범위 조정)
            }


            # 각 색상별 검출 처리
            for color_name, (lower1, upper1, lower2, upper2, box_color) in colors.items():
                # 색상에 따른 마스크 생성
                mask = cv2.inRange(hsv_image, np.array(lower1), np.array(upper1))
                if lower2 is not None and upper2 is not None:
                    mask += cv2.inRange(hsv_image, np.array(lower2), np.array(upper2))

                # 노이즈 제거를 위한 모폴로지 연산
                kernel = np.ones((5, 5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

                # 컨투어 찾기
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # 컨투어를 따라 바운딩 박스 및 색 이름 그리기
                for contour in contours:
                    if cv2.contourArea(contour) > 1000:  # 너무 작은 컨투어는 무시
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                        cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

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
