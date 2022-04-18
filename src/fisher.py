import random
import time

from cv2 import cv2
import numpy as np
from pynput import mouse, keyboard

import cv2utils
from framework.behavior import Behavior
from framework.bot.bot_base	 import BotBase

class Fisher(BotBase):
    def __init__(self):
        super().__init__()
        
        self.bar_area = None
        self.bar_top = 0
        self.bar_left = 0

        # Increase this limit if you have a larger basket
        self.fish_count = 0
        self.fish_limit = 16
        
        self.keep_fishing = True
        
        # Adding spot to update sell thresholds!
        self.sell_threshold = .6
        self.try_search_bar()

    def try_search_bar(self):
        self.mouse.move(800, 800)
        self.mouse.press(mouse.Button.left)
        time.sleep(1.5)
        self.try_execute(self.search_bar, timeout= 20)
        self.mouse.move(0, 0)
        self.mouse.release(mouse.Button.left)

    def search_bar(self):
        frame = np.array(self.screenshot())
        hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        yellow_mask = cv2utils.get_color_mask(hsvframe, (20, 220, 220), (25, 255, 255))
        bar_area = cv2utils.find_area(yellow_mask, min_size= 1500)

        if bar_area is not None:
            bar_area.expand(100, 50)

        self.bar_area = bar_area
        return bar_area != None

    def throw_line(self, left=800, top=800, force=.8):

        jitter = random.randint(-25, 25)
        cast_jitter = random.random()

        print("Throwing line")
        self.click_location(left + jitter,top + jitter, 0)
        time.sleep(.3)
        self.click_location(left + jitter,top + jitter, 2 * force - cast_jitter )
        # print("waiting for the fish to bite")

    def is_bobber(self):

        screenshot = self.screenshot()
        template = self.load_image('bobber.jpg')

        max_loc, max_val = self.template_match(template, screenshot)

        return max_val > .9, max_loc

    def set_bobber(self):
        while True:
            self.throw_line()

            time.sleep(13) #Reset click
            self.click_location(800, 800, 0)
            time.sleep(.5)
            print("finding Bobber")

            is_bobber, pt = self.is_bobber()
            if is_bobber:
                print("Found it!!")
                self.click_location(pt[0], pt[1])
                time.sleep(5)
                return pt[0], pt[1]

    def close_caught_fish(self):
        return self.click_template("YellowX.jpg", .9)

    def sell_fish(self):

        self.push_key(keyboard.Key.up, 2) # Get to store if we are not there...
        self.push_key(keyboard.Key.space, .2) # open store

        if self.click_template("SellBox.jpg", self.sell_threshold, .6):
            print("Looking to for sell")

            if self.click_template("SellFor.jpg", self.sell_threshold, .6):

                print("Looking to for sell Green")
                if self.click_template("Sell.jpg", self.sell_threshold, 0, (100, 0)):
                    self.fish_count = 0
                    
        self.click_location(200,500) # Close store
        time.sleep(.5)
        self.click_location(100,500) # Close store

        self.push_key(keyboard.Key.down, 2) # Go back fishing...

class FishingBehavior(Behavior):

    def __init__(self, fisher : Fisher, run_new_thread=False):
        super().__init__(run_new_thread)
        self.fisher = fisher

    def update(self):
        if self.fisher.close_caught_fish(): # We caught a fish
            self.fisher.fish_count += 1
            print(f"Fish Count: {self.fish_count}")

        if self.fisher.is_bobber():
            print("FISH on SLEEPING!")
            time.sleep(2)
            return

        if self.fisher.fish_count >= self.fisher.fish_limit:
            self.Sell_Fish()
            return

        self.Throw_Line()

        time.sleep(13) #Reset click
        self.fisher.click_location(800, 800, 0)
        time.sleep(.5)

class FishingBarBehavior(Behavior):
    def __init__(self, fisher, run_new_thread=False):
        super().__init__(run_new_thread)
        self.fisher = fisher
    
    def awake(self):
        cv2utils.init_window("main", (800, 100), (-800, 0))
        cv2utils.init_window("red", (800, 100), (-1600, 0))
        cv2utils.init_window("green", (800, 100), (-1600, 130))

    def dispose(self):
        cv2utils.destroy_window("main")
        cv2utils.destroy_window("red")
        cv2utils.destroy_window("green")

    def update(self):
        scr = self.fisher.Screen_Shot(self.fisher.bar_area.x, self.fisher.bar_area.y, self.fisher.bar_area.w, self.fisher.bar_area.h)

        frame = np.array(scr)
        hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # check if is in a valid state
        if self.fisher.fish_count >= self.fisher.fish_limit:
            print("fish count reached limit")
            time.sleep(10)
            return
        
        red_mask = cv2utils.get_color_mask(hsvframe, (0, 150, 150), (10, 255, 255))
        green_mask = cv2utils.get_color_mask(hsvframe, (40, 200, 150), (70, 255, 255))

        # print("showing masks")
        cv2.imshow("red", red_mask)
        cv2.imshow("green", green_mask)

        green_area = cv2utils.find_area(green_mask, 500)
        red_area_1 = cv2utils.find_area(red_mask, 900)
        red_area_2 = cv2utils.find_area(green_mask, 100, 600)
        red_area_2 = None


        if red_area_2 is not None: # and red_area_2 is not None and green_area is not None:
            print(f"found something")
            try:
                green_center = green_area.center
                red_center_1 = red_area_1.center
                red_center_2 = red_area_2.center


                frame_red = cv2.rectangle( frame, red_area_1.min, red_area_1.max, (0, 34, 255), 2 )

                frame_green = cv2.rectangle( frame, green_area.min, green_area.max, (0, 255, 0), 2 )

                distance = int(cv2utils.distance(red_center_1, red_center_2))
                distance2 = int(cv2utils.distance(red_center_2, green_center))
                
                if not np.array_equal(frame_red, frame_green) and distance > 65:
                    if green_center[0] > red_center_2[0] and (red_center_2[0] < red_center_1[0]):
                        self.fisher.mouse.press(mouse.Button.left)
                    elif green_center[0] < red_center_2[0] and (red_center_2[0] > red_center_1[0]) and distance > 65:
                        self.fisher.mouse.release(mouse.Button.left)
                else:
                    if distance2 <= 7 or red_center_2[0] > green_center[0] and red_area_2.x > green_area.x:
                        self.fisher.mouse.release(mouse.Button.left)
                    elif red_center_2[0] < green_center[0] and distance2 > 7 and red_area_2.x < green_area.x:
                        self.fisher.mouse.press(mouse.Button.left)

            except NameError:
                pass

        cv2.imshow("main", frame)
            

        

# Test our classes and functions
# if __name__ == "__main__":
#     print("Unless your testing run main.py")
#     fisher = Fisher()
#     time.sleep(1)
#     fisher.Sell_Fish()