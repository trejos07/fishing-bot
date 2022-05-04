import os
from framework.app_base import AppBase
from fisher import Fisher, FishingBarBehavior, FishingBehavior

class App(AppBase):

	@classmethod 
	def on_start(cls):
		print("app started")
		cls.fisher = Fisher()

		if cls.fisher.bar_area == None:
			print("bar not found")
			cls.quit()
		
		cls.fisher.behaviors.append(FishingBehavior(cls.fisher, True))
		cls.fisher.behaviors.append(FishingBarBehavior(cls.fisher, False))

		for behavior in cls.fisher.behaviors:
			behavior.start()

	@classmethod
	def on_quit(cls):
		cls.fisher.dispose() 
