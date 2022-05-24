from cmath import rect
import time
import cv2
import numpy as np
from framework.geometry.rect import Rect

def init_window(window_name, size, position = (0, 0)):
	blank = np.zeros((size[1], size[0], 3),'uint8')
	cv2.imshow(window_name, blank)
	cv2.moveWindow(window_name, position[0], position[1])
	cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

def destroy_window(window_name):
	cv2.destroyWindow(window_name)

def get_rect(image, rect: Rect):

	if rect and rect.min.x > 0 and rect.min.y > 0 and rect.max.x < image.shape[1] and rect.max.y < image.shape[0]:
		return image[rect.position.y : rect.position.y + rect.size.y, rect.position.x : rect.position.x + rect.size.x]
		
	return None

def get_color_mask(img, lower, upper):
	lower_bound = np.array(lower, np.uint8)
	upper_bound = np.array(upper, np.uint8)
	return cv2.inRange(img, lower_bound, upper_bound)

def find_area(img, min_size, max_size = None, count = 0):
	countours = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
	rect_areas = []
	
	for contour in countours:
		area = cv2.contourArea(contour)
		if min_size < area and (max_size == None or area < max_size):
			rect_areas.append(Rect(*cv2.boundingRect(contour)))

			if count != 0 and len(rect_areas) >= count:
				break

	return rect_areas


rate_limit_counters = {}
def rate_limit(key: str, rate: float) -> bool:
	if key not in rate_limit_counters:
		rate_limit_counters[key] = time.time()
		return True
	
	if time.time() - rate_limit_counters[key] > rate:
		rate_limit_counters[key] = time.time()
		return True
	
	return False
	
def print_rate_limit(msg: str, rate: float):
	if rate_limit(msg, rate):
		print(msg)

