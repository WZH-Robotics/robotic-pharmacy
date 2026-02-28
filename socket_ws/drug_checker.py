import pyrealsense2 as rs
import cv2
import numpy as np

def label_pills_from_realsense():
    # RealSense 카메라 설정
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    # 스트리밍 시작
    pipeline.start(config)
    
    try:
        while True:
            # 프레임 가져오기
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            
            # 이미지를 numpy 배열로 변환
            color_image = np.asanyarray(color_frame.get_data())
            
            # 그레이스케일 변환
            gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
            
            # 이진화 (알약은 흰색, 배경은 검정색)
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            
            # 윤곽선 찾기
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 알약 개수 카운트
            pill_count = 0
            
            # 각 윤곽선을 따라 라벨링 및 경계 상자 그리기
            for contour in contours:
                if cv2.contourArea(contour) > 100:  # 노이즈 제거
                    pill_count += 1
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(color_image, f'Pill {pill_count}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            # 라벨링된 이미지 출력
            cv2.imshow('Labeled Pills', color_image)
            
            # 'q' 키를 누르면 루프 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        # 스트리밍 종료
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    label_pills_from_realsense()
