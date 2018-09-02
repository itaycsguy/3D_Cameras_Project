import sys,os,time,numpy as np,math,logging
# from threading import Thread

"""
Script responsibility about process availability utils
"""

""" Creating new logger object """
def LogBuilder(class_name,debug_mode):
    level = logging.DEBUG
    if not debug_mode:
        level = logging.INFO
    logger = logging.getLogger(class_name)
    logger.setLevel(level)
    st_logger = logging.StreamHandler()
    st_logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    st_logger.setFormatter(formatter)
    logger.addHandler(st_logger)
    return logger


"""" Responsible to create one logger at the same name """
class SingletonLogger():
    counter = 0
    logger = None
    @staticmethod
    def init():
        if not SingletonLogger.logger:
            SingletonLogger.counter += 1
            SingletonLogger.logger = LogBuilder(os.path.basename(__file__),logging.INFO)
        return SingletonLogger.logger

    @staticmethod
    def audit(msg):
        SingletonLogger.logger = SingletonLogger.init()
        if SingletonLogger.counter >= 1:
            SingletonLogger.logger.debug(msg)
        else:
            SingletonLogger.logger.info(msg)


main_dir = None
try:
    SingletonLogger.audit("%%%%%%%%%% ENVIRONMENT VARIABLES FETCHING START %%%%%%%%%%")
    main_dir = os.environ['APP_PATH']
    SingletonLogger.audit("Main Dir Path =" + str(main_dir))
    if not main_dir:
        SingletonLogger.audit("Cannot executing without 'APP_PATH' environment variable definition.")
        input()
        sys.exit(-1)
    main_input_files_dir = os.environ['INPUT_FILES']
    SingletonLogger.audit("Input Files Dir = " + str(main_input_files_dir))
    main_computed_files_dir = os.environ['COMPUTED_FILES']
    SingletonLogger.audit("Computed Files Dir = " + str(main_computed_files_dir))
    IMG_LOGO = main_dir + "\\metadata\\main_logo.png"
    sys.path.append(main_dir + "\\bin\\wrapper")
    SingletonLogger.audit("%%%%%%%%%% ENVIRONMENT VARIABLES FETCHING END %%%%%%%%%%")
except Exception as _:
    SingletonLogger.audit("Cannot executing without 'APP_PATH' environment variable definition.")
from PoseDetector import *