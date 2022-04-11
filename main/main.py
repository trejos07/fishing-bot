import sys
import time
from cv2 import cv2
import numpy as np
import mss
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


def main ():

	mouse = Controller()
	fisher = Fisher()

	bar_left, bar_top = fisher.set_bobber()
	fish_thread = threading.Thread(target=fisher.fish)
	fish_thread.start()

	while True:
		scr = fisher.Screen_Shot(bar_left - 300, bar_top, 800, 100)
		
		frame = np.array(scr)
		hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		if fisher.fish_count >= fisher.fish_limit:
			time.sleep(10)
			continue

		red_mask = get_color_mask(hsvframe, (0, 150, 150), (10, 255, 255))
		green_mask = get_color_mask(hsvframe, (40, 200, 150), (70, 255, 255))

		countours = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

		for contour in countours:
			area = cv2.contourArea(contour)
			if area > 900:
				x1, y1, w1, h1 = cv2.boundingRect(contour)
				frame_red_bar = cv2.rectangle( frame, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2 )
				cv2.putText( frame, "red bar", (x1 + w1, y1 + h1), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), )
				x_red1 = int(x1 + w1 / 2)
				y_red1 = int(y1 + h1 / 2)
				cv2.circle(frame, (x_red1, y_red1), 3, (0, 0, 255), -1)
				try:
					cv2.line(frame, (x_red2, y_red2), (x_red1, y_red1), (0, 0, 255), 2)
				except NameError:
					pass
				cv2.putText( frame, "red bar count: " + str(len(frame_red_bar) - 99), (10, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), )

		for contour in countours:
			area2 = cv2.contourArea(contour)
			if 600 > area2 > 100:
				x1, y1, w1, h1 = cv2.boundingRect(contour)
				frame_red = cv2.rectangle( frame, (x1, y1), (x1 + w1, y1 + h1), (0, 34, 255), 2 )

				x_red2 = int(x1 + w1 / 2)
				y_red2 = int(y1 + h1 / 2)
				cv2.circle(frame, (x_red2, y_red2), 3, (0, 34, 255), -1)
				cv2.putText( frame, "hook", (x1 + w1, y1 + h1), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 34, 255),)
				try:
					distance = int(np.sqrt((x_red2 - x_red1) ** 2 + (y_red2 - y_red1) ** 2))
					distance2 = int(np.sqrt((x_red2 - x_green) ** 2 + (y_red2 - y_green) ** 2))
					if not np.array_equal(frame_red, frame_green) and distance > 65:
						cv2.putText( frame, "red: " + str(distance), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),)
						if x_green > x_red2 and (x_red2 < x_red1):
							if x_green > x_red2:
								cv2.putText( frame, "red: " + str(distance), (10, 40), cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 255), )
							mouse.press(Button.left)
						elif x_green < x_red2 and (x_red2 > x_red1) and distance > 65:
							if x_green < x_red1:
								cv2.putText( frame, "red: " + str(distance), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), )
							mouse.release(Button.left)
					else:
						cv2.putText( frame, "green: " + str(distance2), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), )
						if distance2 <= 7 or x_red2 > x_green and x1 > x2:
							mouse.release(Button.left)
						elif x_red2 < x_green and distance2 > 7 and x1 < x2:
							mouse.press(Button.left)

				except NameError:
					pass

		countours2 = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
		y_green_flag = 0
		for contour in countours2:
			area3 = cv2.contourArea(contour)
			if area3 > 500:
				x2, y2, w2, h2 = cv2.boundingRect(contour)
				frame_green = cv2.rectangle( frame, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 0), 2 )

				x_green = int(x2 + w2 / 2)
				y_green = int(y2 + h2 / 2)

				cv2.circle(frame, (x_green, y_green), 3, (0, 255, 0), -1)
				cv2.putText(frame, "green bar", (x2 + w2, y2 + h2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0),)
				cv2.putText( frame, "green bar count: " + str(len(countours2)), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), )

				try:
					cv2.line(frame, (x_red2, y_red2), (x_green, y_green), (0, 255, 0), 2)
				except NameError:
					pass
		# np.intersect1d(frame_red, frame_green).size
		try:
			if np.array_equal(frame_red, frame_green):
				cv2.putText( frame, f"hooked", (320, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0) )
			else:
				cv2.putText(frame, f"not hooked", (320, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255),)
		except NameError:
			cv2.putText( frame, "not hooked", (320, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255) )
			
		cv2.imshow("main", frame)
		cv2.setWindowProperty("main", cv2.WND_PROP_TOPMOST, 1)

		# Press q to quit program
		if cv2.waitKey(1) & 0xFF == ord("q"):
			fisher.dispose()
			on_quit()
			

