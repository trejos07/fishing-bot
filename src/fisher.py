import random
import time
import traceback

from cv2 import cv2
import numpy as np
from pynput import mouse, keyboard

import cv2utils
from framework.behavior import Behavior
from framework.bot.bot_base	 import BotBase
from framework.geometry.rect import Rect

class Fisher(BotBase):
    def __init__(self):
        super().__init__()
        
        self.bar_area = None
        self.bar_top = 0
        self.bar_left = 0

        # Increase this limit if you have a larger basket
        self.fish_count = 0
        self.fish_limit = 16
        self.fish_on_line = False
        
        self.keep_fishing = True
        
        # Adding spot to update sell thresholds!
        self.sell_threshold = .6

        print("Fisher initialized, trying to find bar")
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
        found_areas = cv2utils.find_area(yellow_mask, min_size= 1500)

        if found_areas is None or len(found_areas) == 0:
            return False

        self.bar_area = found_areas[0]
        self.bar_area.expand(50, 16)
        self.bar_area.position.y -= 4

        return True

    def throw_line(self, left=800, top=800, force=.8):
        jitter = (random.randint(-50, 50), random.randint(-50, 50))
        cast_jitter = random.random()

        print(f"Throwing line at {left}, {top}")
        self.click_location(left + jitter[0], top + jitter[1])
        time.sleep(.33)
        self.click_location(left + jitter[0], top + jitter[1], 2 * force - cast_jitter )

    def throw_line_and_wait_bite(self, min_wait = 13, timeout = 20):
        self.throw_line()
        print("waiting minimun bite time")
        time.sleep(min_wait)
        print("start checking for fish to the bait")

        return self.try_execute(self.try_catch_fish, timeout = timeout)

    def try_catch_fish(self):
        print("searching for hooked image")
        screenshot = self.screenshot()
        hook_templetes = [self.load_image(name) for name in ["Hooked_1.jpg", "Hooked_2.jpg", "Hooked_3.jpg"]]
        pt, val, template = self.multiple_template_match(hook_templetes, screenshot, .5)

        if template is not None:
            self.fish_on_line = True
            self.click_location(pt[0], pt[1])
            return True
            
        return False

    def is_bobber(self):

        screenshot = self.screenshot()
        template = self.load_image('bobber.jpg')

        if template is None:
            print("Could not load bobber template")
            return False

        max_loc, max_val = self.template_match(template, screenshot)

        return max_val > .9

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

        if self.fisher.fish_on_line and self.fisher.is_bobber():
            return

        if self.fisher.close_caught_fish(): # We caught a fish
            self.fish_on_line = False
            self.fisher.fish_count += 1
            print(f"Fish Count: {self.fisher.fish_count}")

        if self.fisher.fish_count >= self.fisher.fish_limit:
            self.Sell_Fish()
            return

        if self.fisher.throw_line_and_wait_bite():
            print("Theres a fish on the line!\tWaitting to catch it...")
            time.sleep(5)

        print("No fish on the line, reset line")
        self.fisher.click_location(800, 800, 0)
        time.sleep(.5)

class FishingBarBehavior(Behavior):
    def __init__(self, fisher : Fisher, run_new_thread : bool = False):
        super().__init__(run_new_thread)
        self.fisher : Fisher = fisher
        self.mousePressed = None
        self.last_bar = None
    
    def awake(self):
        cv2utils.init_window("main", (800, 100), (-800, 0))
        cv2utils.init_window("red", (800, 100), (-1600, 0))
        cv2utils.init_window("green", (800, 100), (-1600, 130))

    def dispose(self):
        cv2utils.destroy_window("main")
        cv2utils.destroy_window("red")
        cv2utils.destroy_window("green")

    def update(self):
        scr = self.fisher.screenshot(*self.fisher.bar_area.position, *self.fisher.bar_area.size)

        frame = np.array(scr)
        hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if not self.fisher.fish_on_line:
            cv2.imshow("main", frame)
            return

        # check if is in a valid state
        if self.fisher.fish_count >= self.fisher.fish_limit:
            print("fish count reached limit")
            time.sleep(10)
            return
        
        red_mask = cv2utils.get_color_mask(hsvframe, (0, 150, 150), (10, 255, 255))
        green_mask = cv2utils.get_color_mask(hsvframe, (40, 200, 150), (70, 255, 255))

        kernal = np.ones((5, 5), "uint8")
        red_mask = cv2.dilate(red_mask, kernal)
        green_mask = cv2.dilate(green_mask, kernal)

        # print("showing masks")
        cv2.imshow("red", red_mask)
        cv2.imshow("green", green_mask)

        hook_areas = cv2utils.find_area(red_mask, 100, 700)
        green_areas = cv2utils.find_area(green_mask, 500)
        red_areas = cv2utils.find_area(red_mask, 900)

        # for g_area in green_areas:
        #     self.draw_rect(frame, g_area, "green", (0, 255, 0))
        # for r_area in red_areas:
        #     self.draw_rect(frame, r_area, "red", (0, 0, 255))
        # for h_area in hook_areas:
        #     self.draw_rect(frame, h_area, "hook", (255, 0, 255))

        hook = Rect.combine_rect_list(hook_areas) if hook_areas else None
        green_bar = Rect.combine_rect_list(green_areas) if green_areas else None
        red_bar = Rect.combine_rect_list(red_areas) if red_areas else None

        self.draw_rect(frame, hook, "hook", (255, 0, 255))
        self.draw_rect(frame, red_bar, "red", (0, 0, 255))
        self.draw_rect(frame, green_bar, "green", (0, 255, 0))

        self.center_hook(hook, green_bar, red_bar)

        cv2.imshow("main", frame)

        
    def center_hook(self, hook : Rect, green_bar : Rect, red_bar : Rect):
        if hook is None:
            cv2utils.print_rate_limit("No hook areas", .5)

        elif green_bar is not None:
            cv2utils.print_rate_limit("Green bar found", .5)

            if self.last_bar == "red":
                self.mousePressed = None
            self.last_bar = "green"

            self.center_hook_in_bars(green_bar, hook, "green")
        elif red_bar is not None:
            cv2utils.print_rate_limit("Red bar found", .5)

            if self.last_bar == "green":
                self.mousePressed = None
            self.last_bar = "red"

            self.center_hook_in_bars(red_bar, hook, "red")

    def draw_rect(self, image, rect : Rect, name : str, color : tuple = (0,0,0)):
        if rect is None:
            return

        cv2.rectangle(image, rect.min, rect.max, color, 2)
        cv2.circle(image, rect.center.as_tuple(), 3, color, 2)
        cv2.putText(image, name, rect.max, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    def center_hook_in_bars(self, bar: Rect, hook : Rect, bar_name : str = ""):

        if bar is None or hook is None:
            return

        dir_to_bar = bar.center - hook.center
        
        if dir_to_bar.x > 0 and not self.mousePressed:
            self.mousePressed = True
            self.fisher.mouse.press(mouse.Button.left)
            print(f"{bar_name} --> hook, pressing mouse: {dir_to_bar.magnitude()}")

        if dir_to_bar.x < 0 and (self.mousePressed or self.mousePressed == None):
            self.mousePressed = False
            self.fisher.mouse.release(mouse.Button.left)
            print(f"hook --> {bar_name}, releasing mouse: {dir_to_bar.magnitude()}")


# Test our classes and functions
# if __name__ == "__main__":
#     print("Unless your testing run main.py")
#     fisher = Fisher()
#     time.sleep(1)
#     fisher.Sell_Fish()
