import math
def calculate_x_pos(x,y, w, h):
    image_x1 = x-320        #left side of bounding box
    image_x2 = image_x1+w   #right side of bounding bot

    image_height = h        #height of object in image
    true_height = 200       #true height of object(Example)

    f = 942.8               #focal length
    k = 1                   # parameter that change pixel to mm
    z = k*f*true_height/image_height  #depth of object

    sqr_f = f*f
    d1d2 = math.sqrt((sqr_f+image_x1*image_x1)*(sqr_f+image_x2*image_x2))
    mid_calc = sqr_f-image_x1*image_x2

    # x_distance = distance to move along axis x
    x_distance = z*math.sqrt((d1d2 - mid_calc)/(d1d2 + mid_calc))
    print(x_distance)
    return x_distance