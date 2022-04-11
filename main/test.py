import os
import sys
from mss import mss
import numpy as np
from cv2 import cv2

def Template_Match( template, image, threshold, debug=False, debug_wait = True, debug_name = "debug"):
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if debug:
            _, w, h = template.shape[::-1]
            debug_result = image.copy()

            loc = np.where( result >= threshold)
            for pt in zip(*loc[::-1]):
                cv2.circle(debug_result, pt, 5, (0,255,255), 2 )
                cv2.circle(debug_result, (int(pt[0] + w), int(pt[1] + h)), 5, (255,0,255), 3)
                cv2.rectangle(debug_result, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

            cv2.imshow(debug_name, debug_result)
            if debug_wait:
                cv2.waitKey(0)

        return (max_loc, max_val)

def Template_Match_Multiple(image, templates, threshold, debug=False):
    for template in templates:

        template_image = 

        pt, val = Template_Match(image, template, threshold, debug, False, f"{template}_debug")

        if debug:
            cv2.waitKey(0)

        if val > threshold:
            return pt, val, template
    
    return None, None, None

def Load_Template(name):
    path = os.path.join(os.path.dirname(__file__), 'img', name)
    cv2.imread(path, cv2.IMREAD_UNCHANGED)


templates = [Load_Template(name) for name in ["Hooked_1.jpg", "Hooked_2.jpg", "Hooked_3.jpg"]]

with mss() as sct:
    while True:
        screen_image = sct.grab({
            'left': 0,
            'top': 0,
            'width': 1920,
            'height': 1080
        })

        screen_image = np.array(screen_image)
        screen_image = cv2.cvtColor(screen_image, cv2.IMREAD_COLOR)

        print('try to match')
        pt, val, template = Template_Match_Multiple(screen_image, templates, 0.5)
        print(f'result: {pt, val, template}')

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Quit")
            cv2.destroyAllWindows()
            sys.exit()