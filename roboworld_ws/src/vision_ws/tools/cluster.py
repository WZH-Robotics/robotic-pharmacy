import cv2
import numpy as np
from sklearn.cluster import KMeans
import pyrealsense2 as rs

def increase_brightness(image, value=50):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = np.clip(v + value, 0, 255)
    final_hsv = cv2.merge((h, s, v))
    return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

def remove_background(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
    return cv2.bitwise_and(image, image, mask=thresh)

def cluster_by_hue(image, n_clusters=4):
    # Convert to HSV and reshape for clustering
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, w, _ = hsv_image.shape
    reshaped_hsv = hsv_image.reshape((h * w, 3))

    # Only use hue for clustering
    hues = reshaped_hsv[:, 0].reshape(-1, 1)

    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(hues)
    clustered_hue = kmeans.labels_.reshape(h, w)

    return clustered_hue, kmeans.cluster_centers_

def label_clusters(image, clustered_hue, cluster_centers):
    output = np.zeros_like(image)
    
    for i, center in enumerate(cluster_centers):
        hue_value = int(center[0])
        
        # Define colors based on hue for visualization (customize as needed)
        if 110 <= hue_value <= 130:  # Purple
            color = (255, 0, 255)
        elif 140 <= hue_value <= 160:  # Pink
            color = (255, 105, 180)
        elif 0 <= hue_value <= 10 or 170 <= hue_value <= 180:  # Red
            color = (0, 0, 255)
        elif 25 <= hue_value <= 35:  # Yellow
            color = (0, 255, 255)
        else:  # Other colors, customize as needed
            color = (255, 255, 255)

        # Apply color to the cluster
        mask = (clustered_hue == i)
        output[mask] = color

    return output

def process_image(image):
    # Step 1: Increase brightness to enhance dark objects
    bright_image = increase_brightness(image, value=50)

    # Step 2: Remove the black cloth and background
    no_background_image = remove_background(bright_image)

    # Step 3: Perform clustering by hue
    clustered_hue, cluster_centers = cluster_by_hue(no_background_image)

    # Step 4: Label the clusters with their respective colors
    labeled_image = label_clusters(no_background_image, clustered_hue, cluster_centers)

    return labeled_image

def initialize_camera():
    # Initialize RealSense pipeline
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)
    return pipeline

def main():
    pipeline = initialize_camera()
    
    try:
        while True:
            # Wait for a new frame
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()

            if not color_frame:
                continue
            
            # Convert to numpy array
            image = np.asanyarray(color_frame.get_data())

            # Process the image
            processed_image = process_image(image)

            # Display the result
            cv2.imshow('Processed Image', processed_image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Stop the pipeline
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
