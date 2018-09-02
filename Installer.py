import os,pip

"""
Class responsibility about installing all environment variables
"""
class Installer():
	from Utils import LogBuilder
	logger = LogBuilder(os.path.basename(__file__), False)

	@staticmethod
	def install():
		dir = str(os.path.dirname(str(os.path.abspath(__file__))))
		dir = dir[:(len(dir) - len("\\bin\\wrapper"))]
		if os.path.exists(dir):
			Installer.logger.info("Found: " + str(dir))
			os.system("SETX APP_PATH " + dir)
		input_files = dir + "\input_files"
		if os.path.exists(input_files):
			Installer.logger.info("Found: " + str(input_files))
			os.system("SETX INPUT_FILES " + input_files)
		computed_files = dir + "\computed_files"
		if os.path.exists(computed_files):
			Installer.logger.info("Found: " + str(computed_files))
			os.system("SETX COMPUTED_FILES " + computed_files)
		Installer.logger.info("Environment variables are installed well.")
		""" There is a python 3.6.5 in our application so we do not need this functionality:
		Installer.logger.info("Installing critical packages...")
		try:
			pip.main(['install', 'opencv-python'])
			pip.main(['install', 'numpy'])
		except Exception as _:
			try:
				os.system("py -m pip install opencv-python")
				os.system("py -m pip install numpy")
			except Exception as _:
				Installer.logger.info("pip was installing the packages, ensure you are using the python standard system!")
		"""
		Installer.logger.info("Completed!")

if __name__ == "__main__":
	Installer.install()