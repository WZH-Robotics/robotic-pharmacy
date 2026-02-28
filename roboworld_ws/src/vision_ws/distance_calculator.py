"""
import math

def calculate_x_pos(x,y,w,h):
    image_x1 = x-320        #left side of bounding box [pxl]
    image_x2 = image_x1+w   #right side of bounding bot [pxl]

    image_height = h        #height of object in image [pxl]
    true_height = 125       #true height of object [mm]

    f = 1.93                #focal length [mm]
    #k_u = 358.21
    k_u = 281.5
    #k_v = 320.00
    k_v = 281.5

    #k_u = 337.20964009      #horizontal scaling factor [pxl/mm]
    #k_v = 432.97146127      #vertical scaling factor [pxl/mm]
    #k_u = 319.5
    #k_v = 239.5
    
    #k_u = 674
    #k_v = 721

    z = math.floor((f*true_height)/(image_height/k_v))  #depth of object [mm]

    sqr_f = f*f
    d1d2 = math.sqrt((sqr_f+image_x1*image_x1)*(sqr_f+image_x2*image_x2))
    mid_calc = sqr_f-image_x1*image_x2

    # x_distance = distance to move along axis x
    x = math.floor(z*math.sqrt((d1d2 - mid_calc)/(d1d2 + mid_calc))/k_u)
    
    #camera_from_mid = 35
    #end-effector_from_camera = 175
    return x-50, z-175

#calculate_x_pos(500,20,100,200)`
"""
import math

def calculate_x_pos(x, y, w, h):
    # Bounding box x-coordinates in image
    x_center = 323.5907
    image_x1 = math.fabs(x - x_center)       # left side of bounding box [pxl] (centered using PPX)
    image_x2 = math.fabs(image_x1 + w)       # right side of bounding box [pxl]

    image_height = h              # height of object in image [pxl]
    true_height = 115             # true height of object [mm]

    # Focal length in pixels from the camera intrinsic data
    fx = 604.5513  # focal length in pixels (x-axis) [pxl/mm]
    fy = 604.5941  # focal length in pixels (y-axis)

    # Calculate depth (z-axis distance) in mm using fy (y-axis focal length)
    z = math.floor((fy * true_height) / image_height)  # depth of object [mm]

    # Calculate distance to move along x-axis using fx
    sqr_f = fx * fx
    d1d2 = math.sqrt((sqr_f + image_x1 * image_x1) * (sqr_f + image_x2 * image_x2))
    mid_calc = sqr_f - image_x1 * image_x2

    # x_distance = distance to move along axis x
    x_distance = math.floor(z / 0.92 * math.sqrt((d1d2 - mid_calc) / (d1d2 + mid_calc)))

    # Subtract 50mm from x to adjust, and 175mm from z for end-effector distance
    if x+w < x_center:
        return -x_distance-40, z-175
    elif x > x_center:
        return x_distance-40, z-175
    else:
        return 0, 0
 
# Example usage:
#x,z = calculate_x_pos(200, 20, 100, 200)
#print(x,z)