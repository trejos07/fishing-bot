from framework.app_base import AppBase
from fisher import Fisher, FishingBarBehavior, FishingBehavior

class App(AppBase):
	@classmethod 
	def on_start(cls):
		cls.fisher = Fisher()

		if cls.fisher.bar_area == None:
			print("bar not found")
			cls.on_quit()
		
		cls.fisher.behaviors.append(FishingBehavior(cls.fisher, True))
		cls.fisher.behaviors.append(FishingBarBehavior(cls.fisher, True))

		for behavior in cls.fisher.behaviors:
			behavior.start()

	@classmethod
	def on_quit(cls):
		cls.fisher.dispose() 

	@classmethod
	def mainloop(cls):	
		print("mainloop")
		super().mainloop()


App.start()
