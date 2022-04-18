import sys
from cv2 import cv2


class AppBase():

	to_update = []

	@classmethod
	def start(cls):
		cls.on_start()
		cls.mainloop()

	@classmethod
	def mainloop(cls):	
		while True:
			for update in cls.to_update:
				update()

			if (cv2.waitKey(1) & 0xFF) == ord("q"):
				cls.quit()

	@classmethod
	def quit(cls):
		cls.on_quit()
		cv2.destroyAllWindows()
		cv2.waitKey(1)
		sys.exit()

	@classmethod
	def on_start(cls):
		pass

	@classmethod
	def on_quit(cls):
		pass