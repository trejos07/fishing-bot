import os
import sys
from mss import mss
import numpy as np
from cv2 import cv2

def template_match(template, image, threshold = 0.9, debug=False, debug_wait = True, debug_name = "debug"):

    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if debug:
        _, w, h = template.shape[::-1]
        debug_result = image.copy()

        loc = np.where( result >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.circle(debug_result, pt, 5, (0,255,255), 2 )
            cv2.circle(debug_result, (int(pt[0] + w / 2), int(pt[1] + h / 2)), 5, (255,0,255), 3)
            cv2.rectangle(debug_result, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

        cv2.imshow(debug_name, debug_result)
        
        if debug_wait:
            cv2.waitKey(0)

    return (max_loc, max_val)

def load_image(name):

    path = os.path.join(name)
    
    print(f"Loading image: {name} from: {path}")
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    return image


template = load_image('D:/Programing/Python/fishing-bot/img/YellowX.jpg')

if template is None:
    print("Template not found")
    sys.exit(1)

img = load_image('D:/Programing/Python/fishing-bot/img/yellow_fish_bug.jpg')

if img is None:
    print("Image not found")
    sys.exit(1)

template_match(template, img, 0.9, True, True, 'debug')

