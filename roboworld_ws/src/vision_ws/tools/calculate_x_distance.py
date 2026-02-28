import math

def calculate_x_pos(x,y,w,h):
    image_x1 = x-320        #left side of bounding box
    image_x2 = image_x1+w   #right side of bounding bot

    image_height = h        #height of object in image
    true_height = 200       #true height of object(Example)

    f = 1.93                #focal length
    k_u = 358.21
    k_v = 320              #pixels per 1mm
    z = (f*true_height)/(image_height/k_v)  #depth of object
    print("z = ",z)

    sqr_f = f*f
    d1d2 = math.sqrt((sqr_f+image_x1*image_x1)*(sqr_f+image_x2*image_x2))
    mid_calc = sqr_f-image_x1*image_x2

    # x_distance = distance to move along axis x
    x_distance = z*math.sqrt((d1d2 - mid_calc)/(d1d2 + mid_calc))/k_u
    print("x_distance = ",x_distance)
    return x_distance

calculate_x_pos(500,20,100,200)