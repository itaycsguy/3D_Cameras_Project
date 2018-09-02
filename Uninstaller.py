import os

"""
Class responsibility about uninstalling all environment variables
"""
class Uninstaller():
    from Utils import LogBuilder
    logger = LogBuilder(os.path.basename(__file__), False)

    @staticmethod
    def uninstall():
        dir = str(os.path.dirname(str(os.path.abspath(__file__))))
        dir = dir[:(len(dir) - len("\\bin\\wrapper"))]
        if os.path.exists(dir):
            Uninstaller.logger.info("Found: " + str(dir))
            os.system("SETX APP_PATH \"\"")
        input_files = dir + "\input_files"
        if os.path.exists(input_files):
            Uninstaller.logger.info("Found: " + str(input_files))
            os.system("SETX INPUT_FILES \"\"")
        computed_files = dir + "\computed_files"
        if os.path.exists(computed_files):
            Uninstaller.logger.info("Found: " + str(computed_files))
            os.system("SETX COMPUTED_FILES \"\"")
        Uninstaller.logger.info("\nEnvironment variables are uninstalled well.")

if __name__ == "__main__":
    Uninstaller.uninstall()