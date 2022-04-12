import sys
import time
from cv2 import cv2
import numpy as np
from pynput.mouse import Button, Controller
import os
from bot import Fisher
import threading

def  on_quit():
	cv2.destroyAllWindows()
	# cv2.waitKey(1)
	sys.exit()

def get_color_mask(img, lower, upper):
	lower_bound = np.array(lower, np.uint8)
	upper_bound = np.array(upper, np.uint8)
	return cv2.inRange(img, lower_bound, upper_bound)


def distance(p1, p2):
	return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
 
def find_area(img, min_size, max_size=None):
	countours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
	for contour in countours:
		area = cv2.contourArea(contour)
		if min_size < area and (max_size is None or area < max_size):
			x, y, w, h = cv2.boundingRect(contour)
			return Rect(x, y, w, h)

class Rect():
	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	
	@property
	def min(self):
		return (self.x, self.y)
	
	@property
	def max(self):
		return (self.x + self.w, self.y + self.h)
	
	@property
	def center(self):
		return (self.x + int(self.w / 2), self.y + int(self.h / 2))


def main ():

	mouse = Controller()
	fisher = Fisher()

	bar_left, bar_top = fisher.set_bobber()
	fish_thread = threading.Thread(target=fisher.fish)
	fish_thread.start()

	red_center_1 = None
	red_center_2 = None
	green_center = None

	while True:
		scr = fisher.Screen_Shot(bar_left - 300, bar_top, 800, 100)

		frame = np.array(scr)
		hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		# check if is in a valid state
		if fisher.fish_count >= fisher.fish_limit:
			time.sleep(10)
			continue

		
		red_mask = get_color_mask(hsvframe, (0, 150, 150), (10, 255, 255))
		green_mask = get_color_mask(hsvframe, (40, 200, 150), (70, 255, 255))


		green_area = find_area(green_mask, 500)
		red_area_1 = find_area(red_mask, 900)
		red_area_2 = find_area(green_mask, 100, 600)

		if red_area_2 is not None:
			try:
				green_center = green_area.center
				red_center_1 = red_area_1.center
				red_center_2 = red_area_2.center


				frame_red = cv2.rectangle( frame, red_area_1.min, red_area_1.max, (0, 34, 255), 2 )

				frame_green = cv2.rectangle( frame, green_area.min, green_area.max, (0, 255, 0), 2 )

				distance = int(distance(red_center_1, red_center_2))
				distance2 = int(distance(red_center_2, green_center))
				
				if not np.array_equal(frame_red, frame_green) and distance > 65:
					if green_center[0] > red_center_2[0] and (red_center_2[0] < red_center_1[0]):
						mouse.press(Button.left)
					elif green_center[0] < red_center_2[0] and (red_center_2[0] > red_center_1[0]) and distance > 65:
						mouse.release(Button.left)
				else:
					if distance2 <= 7 or red_center_2[0] > green_center[0] and red_area_2.x > green_area.x:
						mouse.release(Button.left)
					elif red_center_2[0] < green_center[0] and distance2 > 7 and red_area_2.x < green_area.x:
						mouse.press(Button.left)

			except NameError:
				pass

		cv2.imshow("main", frame)
		cv2.setWindowProperty("main", cv2.WND_PROP_TOPMOST, 1)

		# Press q to quit program
		if cv2.waitKey(1) & 0xFF == ord("q"):
			fisher.dispose()
			on_quit()
			
main()
