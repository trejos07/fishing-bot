import os
import time
import mss
import numpy as np
# import pydirectinput

from cv2 import cv2
from typing import Callable, List
from pynput import mouse, keyboard

from framework.behavior import Behavior
from framework.app_base import AppBase

class BotBase():
    def __init__(self):
        self.stc = mss.mss()
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()
        self.behaviors : List[Behavior] = []
        self.cached_images = {}

        self.screenshot() # Initialize screen shot in the main thread to work in any thread

    def screenshot(self, left=0, top=0, width=1920, height=1080):
        screen_image = self.stc.grab({
            'left': left,
            'top': top,
            'width': width,
            'height': height
        })

        img = np.array(screen_image)
        img = cv2.cvtColor(img, cv2.IMREAD_COLOR)

        return img

    def click_template(self, template_name : str, threshold : float, wait : float = .2, offset = None, debug = False) -> bool:
        template = self.load_image(template_name)

        if template is None:
            print(f"Template {template_name} not found")
            return False

        _, w, h = template.shape[::-1]

        max_loc, max_val = self.template_match(template, self.screenshot(), debug)
                
        if max_val > threshold:

            position_x = int(max_loc[0] + w / 2)
            position_y = int(max_loc[1] + h / 2)

            if offset is not None:
                position_x += offset[0]
                position_y += offset[1]

            self.click_location(position_x, position_y)
            time.sleep(wait)
            return True
 
        return False

    # Compare to images return max value / location
    def template_match(self, template, image, threshold = 0.9, debug=False, debug_wait = True, debug_name = "debug"):

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

    def multiple_template_match(self, templates, image, threshold, debug=False):
        for template in templates:
            pt, val = self.template_match(template, image, threshold, debug, False, f"{template}_debug")

            if debug:
                cv2.waitKey(0)

            if val > threshold:
                return pt, val, template
        
        return None, None, None

# Loading image: YellowX.jpg from: d:\Programing\python\fishing-bot\src\framework\img\YellowX.jpg
    def load_image(self, name):

        if name in self.cached_images:
            return self.cached_images[name]

        path = os.path.join(AppBase.root, 'img', name)
        
        print(f"Loading image: {name} from: {path}")
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        self.cached_images[name] = image

        return image

    def click_location(self, x, y, duration = 0, button = mouse.Button.left):
        self.mouse.position = (x, y)
        self.mouse.press(button)
        time.sleep(duration)
        self.mouse.release(button)
    
    def push_key(self, key, wait=.5):
        self.keyboard.press(key)
        time.sleep(wait)
        self.keyboard.release(key)

    def push_keys(self, keys, wait=.5):
        for key in keys:
            self.keyboard.press(key)

        time.sleep(wait)

        for key in keys:   
            self.keyboard.release(key)
    
    def try_execute(self, command : Callable[[], bool], timeout = 1) -> bool:
        if timeout <= 0:
            return
        
        timeout += time.time()

        while time.time() < timeout:
            result = command()

            if result:
                return True

        return False

    def refresh_page(self):
        self.push_key(keyboard.Key.f5)
        time.sleep(1)
        self.push_key(keyboard.Key.enter, 0)

    def dispose(self):
        self.stc.close()
        
        for behavior in self.behaviors:
            behavior.stop()
        
        self.behaviors = []
