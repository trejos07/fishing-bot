from typing import Callable
from cv2 import cv2
import mss
import numpy as np
import os
import time
#from pynput.mouse import Button, Controller
from pynput import mouse, keyboard
import random
import pydirectinput

class Bot:
    def __init__(self):
        self.stc = mss.mss()
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()

        path = os.path.dirname(os.path.dirname(__file__))
        self.img_path = os.path.join(path, 'img')

        self.Screen_Shot() # Initialize screen shot in the main thread to work in any thread

    def Screen_Shot(self, left=0, top=0, width=1920, height=1080):
        screen_image = self.stc.grab({
            'left': left,
            'top': top,
            'width': width,
            'height': height
        })

        img = np.array(screen_image)
        img = cv2.cvtColor(img, cv2.IMREAD_COLOR)

        return img

    def Click_Template(self, template_name : str, threshold : float, wait : float = .2, offset = None, debug = False) -> bool:
        template = self.Load_Image(template_name)
        _, w, h = template.shape[::-1]

        max_loc, max_val = self.Template_Match(template, self.Screen_Shot(), debug)
                
        if max_val > threshold:

            position_x = int(max_loc[0] + w / 2)
            position_y = int(max_loc[1] + h / 2)

            if offset is not None:
                position_x += offset[0]
                position_y += offset[1]

            self.Click_Location(position_x, position_y)
            time.sleep(wait)
            return True
 
        return False

    # Compare to images return max value / location
    def Template_Match(self, template, image, threshold = 0.9, debug=False, debug_wait = True, debug_name = "debug"):
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

    def Template_Match_Multiple(self, templates, image, threshold, debug=False):
        for template in templates:
            pt, val = self.Template_Match(template, image, threshold, debug, False, f"{template}_debug")

            if debug:
                cv2.waitKey(0)

            if val > threshold:
                return pt, val, template
        
        return None, None, None

    def Load_Image(self, name):
        path = os.path.join(os.path.dirname(__file__), 'img', name)
        return cv2.imread(path, cv2.IMREAD_UNCHANGED)

    def Click_Location(self, x, y, duration=0):
        pydirectinput.moveTo(x, y)
        pydirectinput.mouseDown()
        time.sleep(duration)
        pydirectinput.mouseUp()
    
    def Push_key(self, key, wait=.5):
        self.keyboard.press(key)
        time.sleep(wait)
        self.keyboard.release(key)
    
    def Try_Execute(self, command : Callable[[], bool], timeout = 1) -> bool:
        if timeout <= 0:
            return
        
        timeout += time.time()

        while time.time() < timeout:
            result = command()

            if result:
                return True

        return False

class Fisher(Bot):
    def __init__(self):
        super().__init__()
        self.bar_top = 0
        self.bar_left = 0

        # Increase this limit if you have a larger basket
        self.fish_count = 0
        self.fish_limit = 16
        
        self.keep_fishing = True
        
        # Adding spot to update sell thresholds!
        self.sell_threshold = .6

    def fish(self):
        while self.keep_fishing:
            if self.close_caught_fish():
                # We caught a fish
                self.fish_count += 1
                print(f"Fish Count: {self.fish_count}")
            if self.is_bobber():
                print("FISH on SLEEPING!")
                time.sleep(2)
                continue
            if self.fish_count >= self.fish_limit:
                    self.Sell_Fish()
                    continue
            #Reset click
            jitter = random.randint(-25, 25)
            cast_jitter = random.random()

            pydirectinput.click(800 + jitter,800 + jitter)
            time.sleep(.5)
            self.Click_Location(800 + jitter,800 + jitter,.2 + cast_jitter)
            print("Throwing line")
            time.sleep(13)
            self.Click_Location(800 + jitter,800 + jitter,.5)
            time.sleep(.5)

    def Throw_Line(self, left=800, top=800, force=.8):

        jitter = random.randint(-25, 25)
        cast_jitter = random.random()

        # pydirectinput.click(800 + jitter,800 + jitter)
        # time.sleep(.5)
        print("Throwing line")
        self.Click_Location(left + jitter,top + jitter, 2 * force - cast_jitter )
        print("waiting for the fish to bite")

        # time.sleep(13)
        # self.Click_Location(800 + jitter,800 + jitter,.5)

    def is_bobber(self):
        template = self.Load_Image('bobber.jpg')
        max_loc, max_val = self.Template_Match(template, self.Screen_Shot())
        return max_val > .9, max_loc

    def set_bobber(self):
        while True:
            print("Reset Click.")
            pydirectinput.click(800,800)
            time.sleep(.6)
            self.Click_Location(800,800,1)
            time.sleep(13)
            pydirectinput.click(800,800)
            time.sleep(.6)
            print("finding Bobber")

            is_bobber, pt = self.is_bobber()
            if is_bobber:
                print("Found it!!")
                return pt[1] - 20, pt[0]

            print(f"Found: {is_bobber} sleeping")

    def close_caught_fish(self):
        return self.Click_Template("YellowX.jpg", .9)

    def Sell_Fish(self):

        # Get to store if we are not there...
        self.Push_key(keyboard.Key.up, 2)
        self.Push_key(keyboard.Key.space, .2)

        if self.Click_Template("SellBox.jpg", self.sell_threshold, .6):
            print("Looking to for sell")

            if self.Click_Template("SellFor.jpg", self.sell_threshold, .6):

                print("Looking to for sell Green")
                if self.Click_Template("Sell.jpg", self.sell_threshold, 0, (100, 0)):
                    self.fish_count = 0
                    

        self.Click_Location(200,500)
        time.sleep(.5)
        self.Click_Location(100,500)
        # Go back fishing...
        self.Push_key(keyboard.Key.down, 2)
    
    

    def start_fresh(self):
        time.sleep(5)
        self.keyboard.press(keyboard.Key.ctrl)
        self.keyboard.press('r')
        time.sleep(1)
        self.keyboard.release(keyboard.Key.ctrl)
        self.keyboard.release('r')
        time.sleep(1)
        self.keyboard.press(keyboard.Key.enter) 
        self.keyboard.release(keyboard.Key.enter)
    
    def dispose(self):
        self.keep_fishing = False
        

# Test our classes and functions
if __name__ == "__main__":
    print("Unless your testing run main.py")
    fisher = Fisher()
    time.sleep(1)
    fisher.Sell_Fish()