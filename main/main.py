import sys
import time
from cv2 import cv2
import numpy as np
from pynput.mouse import Button, Controller
import os
from bot import Fisher
from rect import Rect
import threading
import cv2utils

from main.rect import Rect

class App():
	def __init__(self):
		self.on_update = None
		self.on_quit = None

	def start(self):	
		while True:

			if self.on_update != None:
				self.on_update()

			if (cv2.waitKey(1) & 0xFF) == ord("q"):
				if self.on_quit != None:
					self.on_quit()
				quit()

	def quit():
		cv2.destroyAllWindows()
		cv2.waitKey(1)
		sys.exit()


def on_quit():
	cv2.destroyAllWindows()
	cv2.waitKey(1)
	sys.exit()


def distance(p1, p2):
	return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def search_bar(fisher : Fisher):
	frame = np.array(fisher.Screen_Shot())
	hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	yellow_mask = cv2utils.get_color_mask(hsvframe, (20, 220, 220), (25, 255, 255))
	bar_area = cv2utils.find_area(yellow_mask, min_size= 1500)

	if bar_area is not None:
		bar_area.expand(100, 50)

	fisher.bar_area = bar_area
	return bar_area != None

def try_search_bar(fisher : Fisher):
	fisher.mouse.move(800, 800)
	fisher.mouse.press(Button.left)
	time.sleep(1.5)
	fisher.Try_Execute(lambda: search_bar(fisher), timeout= 20)
	fisher.mouse.move(0, 0)
	fisher.mouse.release(Button.left)



def main ():

	mouse = Controller()
	fisher = Fisher()

	try_search_bar(fisher)

	if fisher.bar_area == None:
		print("bar not found")
		on_quit()

	cv2utils.init_window("main", (800, 100), (-800, 0))
	cv2utils.init_window("red", (800, 100), (-1600, 0))
	cv2utils.init_window("green", (800, 100), (-1600, 130))

	fish_thread = threading.Thread(target=fisher.fish)
	fish_thread.start()

	red_center_1 = None
	red_center_2 = None
	green_center = None

	while True:

		scr = fisher.Screen_Shot(fisher.bar_area.x, fisher.bar_area.y, fisher.bar_area.w, fisher.bar_area.h)

		frame = np.array(scr)
		hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

		# check if is in a valid state
		if fisher.fish_count >= fisher.fish_limit:
			print("fish count reached limit")
			time.sleep(10)
			continue
		
		red_mask = cv2utils.get_color_mask(hsvframe, (0, 150, 150), (10, 255, 255))
		green_mask = cv2utils.get_color_mask(hsvframe, (40, 200, 150), (70, 255, 255))
		yellow_mask = cv2utils.get_color_mask(hsvframe, (34, 200, 220), (34, 255, 255))

		# print("showing masks")
		cv2.imshow("red", red_mask)
		cv2.imshow("green", green_mask)
		cv2.imshow("yellow", green_mask)

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

		# Press q to quit program
		if (cv2.waitKey(1) & 0xFF) == ord("q"):
			fisher.dispose()
			on_quit()

app = App()
fisher = Fisher()
app.on_update = main
app.on_quit = fisher.dispose
app.start()
