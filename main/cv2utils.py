import cv2
import numpy as np
from rect import Rect

def init_window(window_name, size, position = (0, 0)):
	blank = np.zeros((size[1], size[0], 3),'uint8')
	cv2.imshow(window_name, blank)
	cv2.moveWindow(window_name, position[0], position[1])
	cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

def get_color_mask(img, lower, upper):
	lower_bound = np.array(lower, np.uint8)
	upper_bound = np.array(upper, np.uint8)
	return cv2.inRange(img, lower_bound, upper_bound)

def find_area(img, min_size, max_size=None):
	countours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

	for contour in countours:
		area = cv2.contourArea(contour)
		if min_size < area and (max_size == None or area < max_size):
			x, y, w, h = cv2.boundingRect(contour)
			return Rect(x, y, w, h)
	
	return None