# import cv2
# import numpy as np

# def label_colored_pills_with_noise_reduction():
#     cap = cv2.VideoCapture(0)
    
#     if not cap.isOpened():
#         print("카메라를 열 수 없습니다.")
#         return
    
#     try:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 print("프레임을 가져올 수 없습니다.")
#                 break

#             hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

#             # 색상 범위 설정
#             lower_white = np.array([0, 0, 200])
#             upper_white = np.array([255, 255, 255])

#             mask_white = cv2.inRange(hsv_image, lower_white, upper_white)

#             # 1. Gaussian Blur 적용 (노이즈 제거)
#             blurred = cv2.GaussianBlur(mask_white, (9, 9), 0)

#             # 2. 모폴로지 연산 적용
#             kernel = np.ones((7, 7), np.uint8)
#             morph = cv2.morphologyEx(blurred, cv2.MORPH_OPEN, kernel)

#             # 3. Canny Edge Detection 적용
#             edges = cv2.Canny(morph, 100, 250)

#             # 컨투어 찾기 및 필터링
#             contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#             MIN_AREA = 1000
#             for contour in contours:
#                 if cv2.contourArea(contour) > MIN_AREA:
#                     x, y, w, h = cv2.boundingRect(contour)
#                     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#             # 결과 이미지 출력
#             cv2.imshow('Pill Detection with Noise Reduction', frame)
#             cv2.imshow('Edges', edges)

#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
    
#     finally:
#         cap.release()
#         cv2.destroyAllWindows()

# label_colored_pills_with_noise_reduction()

########## 일단 이거 성공적임 ########## 근데 수정이 필요
# import cv2
# import numpy as np

# def label_colored_pills_with_noise_reduction():
#     cap = cv2.VideoCapture(0)
    
#     if not cap.isOpened():
#         print("카메라를 열 수 없습니다.")
#         return
    
#     try:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 print("프레임을 가져올 수 없습니다.")
#                 break

#             # HSV 색상 공간으로 변환
#             hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

#             # 1. 각 색상에 대한 범위 설정 (빨강, 주황, 노랑, 초록, 파랑, 흰색)
#             lower_red1 = np.array([0, 50, 50])
#             upper_red1 = np.array([10, 255, 255])
#             lower_red2 = np.array([170, 50, 50])
#             upper_red2 = np.array([180, 255, 255])

#             lower_orange = np.array([10, 100, 100])
#             upper_orange = np.array([25, 255, 255])

#             lower_yellow = np.array([25, 100, 100])
#             upper_yellow = np.array([35, 255, 255])

#             lower_green = np.array([35, 50, 50])
#             upper_green = np.array([85, 255, 255])

#             lower_blue = np.array([90, 50, 50])
#             upper_blue = np.array([130, 255, 255])

#             lower_white = np.array([0, 0, 200])
#             upper_white = np.array([255, 255, 255])

#             # 2. 색상에 따른 마스크 생성
#             mask_red = cv2.inRange(hsv_image, lower_red1, upper_red1) + cv2.inRange(hsv_image, lower_red2, upper_red2)
#             mask_orange = cv2.inRange(hsv_image, lower_orange, upper_orange)
#             mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
#             mask_green = cv2.inRange(hsv_image, lower_green, upper_green)
#             mask_blue = cv2.inRange(hsv_image, lower_blue, upper_blue)
#             mask_white = cv2.inRange(hsv_image, lower_white, upper_white)

#             # 마스크들을 합침
#             combined_mask = mask_red + mask_orange + mask_yellow + mask_green + mask_blue + mask_white

#             # 3. Gaussian Blur 적용
#             blurred = cv2.GaussianBlur(combined_mask, (5, 5), 0)

#             # 4. Canny Edge Detection 적용
#             edges = cv2.Canny(blurred, 100, 200)

#             # 5. 컨투어 찾기 및 필터링
#             contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#             MIN_AREA = 500  # 면적 임계값
#             for contour in contours:
#                 if cv2.contourArea(contour) > MIN_AREA:
#                     x, y, w, h = cv2.boundingRect(contour)
#                     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#             # 결과 이미지 출력
#             cv2.imshow('Pill Detection with Noise Reduction', frame)
#             cv2.imshow('Edges', edges)

#             # 'q' 키를 누르면 종료
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
    
#     finally:
#         cap.release()
#         cv2.destroyAllWindows()

# # 함수 실행
# label_colored_pills_with_noise_reduction()
###################################


import pyrealsense2 as rs
import cv2
import numpy as np

def label_colored_pills_with_noise_reduction():
    # 카메라 스트림 열기 (기본 카메라)
    #cap = cv2.VideoCapture(0)
    # RealSense 카메라 설정
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    # 스트리밍 시작
    pipeline.start(config)

    #if not cap.isOpened():
    #    print("카메라를 열 수 없습니다.")
    #    return
    
    try:
        while True:
            # 프레임 가져오기
            frames = pipeline.wait_for_frames()
            #color_frame = frames.get_color_frame()
            #if not color_frame:
            #    continue
          
            # HSV 색상 공간으로 변환
            hsv_image = cv2.cvtColor(frames, cv2.COLOR_BGR2HSV)

            # 1. 각 색상에 대한 범위 설정 (빨강, 주황, 노랑, 초록, 파랑, 흰색)
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])

            lower_orange = np.array([10, 100, 100])
            upper_orange = np.array([25, 255, 255])

            lower_yellow = np.array([25, 100, 100])
            upper_yellow = np.array([35, 255, 255])

            lower_green = np.array([35, 50, 50])
            upper_green = np.array([85, 255, 255])

            lower_blue = np.array([90, 50, 50])
            upper_blue = np.array([130, 255, 255])

            lower_white = np.array([0, 0, 200])
            upper_white = np.array([255, 255, 255])

            # 2. 색상에 따른 마스크 생성
            mask_red = cv2.inRange(hsv_image, lower_red1, upper_red1) + cv2.inRange(hsv_image, lower_red2, upper_red2)
            mask_orange = cv2.inRange(hsv_image, lower_orange, upper_orange)
            mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
            mask_green = cv2.inRange(hsv_image, lower_green, upper_green)
            mask_blue = cv2.inRange(hsv_image, lower_blue, upper_blue)
            mask_white = cv2.inRange(hsv_image, lower_white, upper_white)

            # 마스크들을 합침
            combined_mask = mask_red + mask_orange + mask_yellow + mask_green + mask_blue + mask_white

            # 3. Gaussian Blur 적용 (노이즈 제거)
            blurred = cv2.GaussianBlur(combined_mask, (9, 9), 0)

            # 4. 모폴로지 연산 적용 (노이즈 감소)
            kernel = np.ones((5, 5), np.uint8)
            morph = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)  # 작은 구멍 채우기
            morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)  # 작은 노이즈 제거

            # 5. Canny Edge Detection 적용
            edges = cv2.Canny(morph, 100, 250)

            # 6. 컨투어 찾기 및 필터링 (컨투어 면적 필터 추가)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            MIN_AREA = 1000  # 작은 노이즈 제거를 위한 최소 면적 설정
            for contour in contours:
                if cv2.contourArea(contour) > MIN_AREA:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frames, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # 결과 이미지 출력
            cv2.imshow('Pill Detection with Noise Reduction', frames)
            cv2.imshow('Edges', edges)

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

# 함수 실행
label_colored_pills_with_noise_reduction()

