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
        self.bar_area.y -= 4

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
        self.mousePressed = False
    
    def awake(self):
        cv2utils.init_window("main", (800, 100), (-800, 0))
        cv2utils.init_window("red", (800, 100), (-1600, 0))
        cv2utils.init_window("green", (800, 100), (-1600, 130))

    def dispose(self):
        cv2utils.destroy_window("main")
        cv2utils.destroy_window("red")
        cv2utils.destroy_window("green")

    def draw_rect(self, image, rect : Rect, name : str, color : tuple = (0,0,0)):
        if rect is None:
            return

        cv2.rectangle(image, rect.min, rect.max, color, 2)
        cv2.circle(image, rect.center, 3, color, 2)
        cv2.putText(image, name, rect.max, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    def new_update(self):
        scr = self.fisher.screenshot(self.fisher.bar_area.x, self.fisher.bar_area.y, self.fisher.bar_area.w, self.fisher.bar_area.h)

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

        #make a frame cope to debug the areas
        frame_copy = frame.copy()

        for g_area in green_areas:
            self.draw_rect(frame_copy, g_area, "green", (0, 255, 0))
        for r_area in red_areas:
            self.draw_rect(frame_copy, r_area, "red", (0, 0, 255))
        for h_area in hook_areas:
            self.draw_rect(frame_copy, h_area, "hook", (255, 0, 255))

        if hook_areas is None:
            print("No hook areas")
            return

        # cv2.imshow("main", frame_copy)
        # time.sleep(.2)
        # return

        red_bar = red_areas[-1] if red_areas else None
        red_center = red_bar.center if red_areas else None

        green_bar = green_areas[-1] if green_areas else None
        green_center = green_bar.center if green_areas else None

        for hook in hook_areas:
            hook_center = hook.center

            frame_red = cv2.rectangle( frame, red_bar.min, red_bar.max, (0, 0, 0), 2 ) if red_areas else frame

            frame_green = cv2.rectangle( frame, green_bar.min, green_bar.max, (0, 0, 0), 2 ) if green_areas else frame

            distance = int(cv2utils.distance(hook_center, red_center)) if red_center else 0
            distance2 = int(cv2utils.distance(hook_center, green_center)) if green_center else 0
            
            if not np.array_equal(frame_red, frame_green) and distance > 65:
                if green_center.x > hook_center.x and (hook_center.x < red_center.x):
                    cv2.putText(frame_copy,"red: " + str(distance),(10, 40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0, 0, 255),)
                    if not self.mousePressed:
                        print("press mouse button =")
                        self.mousePressed = True
                        self.fisher.mouse.press(mouse.Button.left)
                elif green_center.x < hook_center.x and (hook_center.x > red_center.x) and distance > 65:
                    cv2.putText( frame_copy, "red: " + str(distance), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))

                    if self.mousePressed:
                        print("release mouse button =")
                        self.mousePressed = False
                        self.fisher.mouse.release(mouse.Button.left)
            else:
                cv2.putText(frame_copy, "green: " + str(distance2), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0))
                if distance2 <= 7 or hook_center.x > green_center.x and hook.x > green_bar.x:
                    if self.mousePressed:
                        print("release mouse button")
                        self.mousePressed = False
                        self.fisher.mouse.release(mouse.Button.left)
                elif hook_center.x < green_center.x and distance2 > 7 and hook.x < green_bar.x:
                    if not self.mousePressed:
                        print("press mouse button")
                        self.mousePressed = True
                        self.fisher.mouse.press(mouse.Button.left)

        cv2.imshow("main", frame_copy)

    def update(self):
        self.new_update()

    def old_update(self):
        scr = self.fisher.screenshot(self.fisher.bar_area.x, self.fisher.bar_area.y, self.fisher.bar_area.w, self.fisher.bar_area.h)

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

        cv2.imshow("red", red_mask)
        cv2.imshow("green", green_mask)

        countours = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

        for contour in countours:
            area = cv2.contourArea(contour)
            if area > 900:
                x1, y1, w1, h1 = cv2.boundingRect(contour)
                frame_red_bar = cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)
                cv2.putText(frame,"red bar",(x1 + w1, y1 + h1),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0, 0, 255))
                x_red1 = int(x1 + w1 / 2)
                y_red1 = int(y1 + h1 / 2)
                cv2.circle(frame, (x_red1, y_red1), 3, (0, 0, 255), -1)
                try:
                    cv2.line(frame, (x_hook, y_hook), (x_red1, y_red1), (0, 0, 255), 2)
                except NameError:
                    pass
                cv2.putText(frame, "red bar count: " + str(len(frame_red_bar) - 99), (10, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))


        countours2 = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        y_green_flag = 0
        
        for contour in countours2:
            area3 = cv2.contourArea(contour)
            if area3 > 500:
                x2, y2, w2, h2 = cv2.boundingRect(contour)
                frame_green = cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)

                x_green = int(x2 + w2 / 2)
                y_green = int(y2 + h2 / 2)

                cv2.circle(frame, (x_green, y_green), 3, (0, 255, 0), -1)
                cv2.putText(frame, "green bar", (x2 + w2, y2 + h2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0))
                cv2.putText(frame, "green bar count: " + str(len(countours2)), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0))

                try:
                    cv2.line(frame, (x_hook, y_hook), (x_green, y_green), (0, 255, 0), 2)

                except NameError:
                    pass

        for contour in countours:
            area2 = cv2.contourArea(contour)
            if 600 > area2 > 100:
                x1, y1, w1, h1 = cv2.boundingRect(contour)
                frame_red = cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 34, 255), 2)
                x_hook = int(x1 + w1 / 2)
                y_hook = int(y1 + h1 / 2)
                cv2.circle(frame, (x_hook, y_hook), 3, (0, 34, 255), -1)
                cv2.putText(frame, "hook", (x1 + w1, y1 + h1), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 34, 255))

                try:
                    print("check distance")
                    distance = int(np.sqrt((x_hook - x_red1) ** 2 + (y_hook - y_red1) ** 2))
                    distance2 = int(np.sqrt((x_hook - x_green) ** 2 + (y_hook - y_green) ** 2))
                    if not np.array_equal(frame_red, frame_green) and distance > 65:
                        cv2.putText(frame,"red: " + str(distance),(10, 40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0, 0, 255),)
                        if x_green > x_hook and (x_hook < x_red1):
                            if x_green > x_hook:
                                cv2.putText( frame, "red: " + str(distance), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))
                            print("try click")
                            self.fisher.mouse.press(mouse.Button.left)
                            print("press click")

                        elif x_green < x_hook and (x_hook > x_red1) and distance > 65:
                            if x_green < x_red1:
                                cv2.putText( frame, "red: " + str(distance), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))
                            print("try click")
                            self.fisher.mouse.release(mouse.Button.left)
                            print("release click")

                    else:
                        cv2.putText(frame, "green: " + str(distance2), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0))
                        if distance2 <= 7 or x_hook > x_green and x1 > x2:
                            print("try click")
                            self.fisher.mouse.release(mouse.Button.left)
                            print("release click")

                        elif x_hook < x_green and distance2 > 7 and x1 < x2:
                            print("try click")                            
                            self.fisher.mouse.press(mouse.Button.left)
                            print("press click")

                except Exception as e: 
                    print(e)
                    traceback.print_exc()


        countours2 = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        y_green_flag = 0
        for contour in countours2:
            area3 = cv2.contourArea(contour)
            if area3 > 500:
                x2, y2, w2, h2 = cv2.boundingRect(contour)
                frame_green = cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2)

                x_green = int(x2 + w2 / 2)
                y_green = int(y2 + h2 / 2)

                cv2.circle(frame, (x_green, y_green), 3, (0, 255, 0), -1)
                cv2.putText(frame, "green bar", (x2 + w2, y2 + h2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0))
                cv2.putText(frame, "green bar count: " + str(len(countours2)), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0))

                try:
                    cv2.line(frame, (x_hook, y_hook), (x_green, y_green), (0, 255, 0), 2)

                except NameError:
                    pass
        # try:
        #     if np.array_equal(frame_red, frame_green):
        #         cv2.putText(frame, f"hooked", (320, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0))
        #     else:
        #         cv2.putText(frame, f"not hooked", (320, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))
        # except NameError:
        #     cv2.putText(frame, "not hooked", (320, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))

        cv2.imshow("main", frame)
        # cv2.setWindowProperty("main", cv2.WND_PROP_TOPMOST, 1)


# Test our classes and functions
# if __name__ == "__main__":
#     print("Unless your testing run main.py")
#     fisher = Fisher()
#     time.sleep(1)
#     fisher.Sell_Fish()
