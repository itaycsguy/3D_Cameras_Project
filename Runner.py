import cv2,time,datetime,argparse,csv,shutil,os,math,numpy as np
from CamRGBenv import *
from Utils import LogBuilder
from threading import Thread

"""
This class responsibility is about the execution time computation and matching between people around the circle relationship
Used as main class for each camera that going to be executed
"""


class Runner:
    local_logger = LogBuilder(__name__, False)

    size_arr1 = -1
    #here we save the final frames (the results)
    Results = [None] * 2000
    #each array have the frames for each player
    arr1 = [math.inf] * 2000
    arr2 = [math.inf] * 2000
    arr3 = [math.inf] * 2000
    arr4 = [math.inf] * 2000
    #the frames are synchronized and sorted by the time stamp
    arranged_arr2 = [math.inf] * 2000
    arranged_arr3 = [math.inf] * 2000
    arranged_arr4 = [math.inf] * 2000
    # set the image's size
    AllImSize = (1350, 700)

    # set for each person his own camera
    port = 0
    cam1 = cv2.VideoCapture(port)
    cam2 = cv2.VideoCapture(port + 1)
    cam3 = cv2.VideoCapture(port + 2)
    cam4 = cv2.VideoCapture(port + 3)


    #This Function reset the arrays
    #in case we want to get another frames and save them in those arrays
    @staticmethod
    def reset_arrays():
        Runner.arr1 = [math.inf] * 2000
        Runner.arr2 = [math.inf] * 2000
        Runner.arr3 = [math.inf] * 2000
        Runner.arr4 = [math.inf] * 2000
        Runner.arranged_arr2 = [math.inf] * 2000
        Runner.arranged_arr3 = [math.inf] * 2000
        Runner.arranged_arr4 = [math.inf] * 2000


    #Here we get the Frame's name and return the number for the player whose face in the current frame
    @staticmethod
    def GetPlayerNum(FrameName):
        arr = FrameName.rsplit('_', 1)
        PlayerNum = int(arr[0])
        return PlayerNum


    #Here we get the Frame's name and return the time that this frame has been taken
    @staticmethod
    def GetFrameTime(FrameName):
        x = FrameName.rsplit('_', 1)
        FrameN = x[1]
        y = FrameN.rsplit('.', 1)
        FrameTime = y[0]
        return float(FrameTime)


    #Return the absolute distance between two numbers
    @staticmethod
    def GetDistance(num1, num2):
        if (num1 - num2) < 0:
            return (num2 - num1)
        else:
            return (num1 - num2)


    #This Function synchrone the arrays with each other
    #So we take each frame and append to it the nearest frame (by time)
    @staticmethod
    def arrange_data():
        Runner.local_logger.info("Running into " + str(__name__) + ":arrange_data")
        Runner.local_logger.debug("The arrays arrangement:")
        for x in range(0, 2000):
            if (Runner.arr1[x] == math.inf):
                break

            #Here we look for the minimum distance
            min2 = Runner.GetDistance(Runner.arr1[x], Runner.arr2[0])
            index2 = 0

            min3 = Runner.GetDistance(Runner.arr1[x], Runner.arr3[0])
            index3 = 0

            min4 = Runner.GetDistance(Runner.arr1[x], Runner.arr4[0])
            index4 = 0

            for y in range(0, 2000): # finding for each frame his closest frame (by time)
                if Runner.arr2[y] != math.inf:
                    if Runner.GetDistance(Runner.arr1[x], Runner.arr2[y]) < min2:
                        min2 = Runner.GetDistance(Runner.arr1[x], Runner.arr2[y])
                        index2 = y

                    if Runner.GetDistance(Runner.arr1[x], Runner.arr3[y]) < min3:
                        min3 = Runner.GetDistance(Runner.arr1[x], Runner.arr3[y])
                        index3 = y

                    if Runner.GetDistance(Runner.arr1[x], Runner.arr4[y]) < min4:
                        min4 = Runner.GetDistance(Runner.arr1[x], Runner.arr4[y])
                        index4 = y
            #Then put all the arranged frames in this arrays
            Runner.arranged_arr2[x] = Runner.arr2[index2]
            Runner.arranged_arr3[x] = Runner.arr3[index3]
            Runner.arranged_arr4[x] = Runner.arr4[index4]

            Runner.local_logger.debug(str(x) + " - " + str(index2) + " - " + str(index3) + " - " + str(index4))
        Runner.local_logger.info("The data has been arranged successfully!")


    #Here we save the frames' name in the arrays for each player
    @staticmethod
    def Get_Frames_Names():
        Runner.local_logger.info("Running into " + str(__name__) + ":Get_Frames_Names")
        Runner.reset_arrays()
        index_1 = 0
        index_2 = 0
        index_3 = 0
        index_4 = 0
        IsEmpty = True
        for file in os.listdir(main_input_files_dir):
            #the file who have the frames
            file_path = main_input_files_dir + "\\" + file
            if not os.path.isdir(file_path):
                IsEmpty = False
                if ((file[1] == '_') & (file[2] != 'L')):   # We check whether the file is an real-time image
                    if (Runner.GetPlayerNum(file) == 1):    # This frame belong to the first Player
                        Runner.arr1[index_1] = Runner.GetFrameTime(file)
                        index_1 += 1
                    if (Runner.GetPlayerNum(file) == 2):    # This frame belong to the second Player
                        Runner.arr2[index_2] = Runner.GetFrameTime(file)
                        index_2 += 1
                    if (Runner.GetPlayerNum(file) == 3):    # This frame belong to the third Player
                        Runner.arr3[index_3] = Runner.GetFrameTime(file)
                        index_3 += 1
                    if (Runner.GetPlayerNum(file) == 4):    ## This frame belong to the fourth Player
                        Runner.arr4[index_4] = Runner.GetFrameTime(file)
                        index_4 += 1
        #here we check if the input_files is Empty
        if IsEmpty == True:
            Runner.local_logger.info("The input_files directory is Empty!")
            Runner.local_logger.info("Get frames and their computations from third party or using out system real time recording.")
            return -1
        #here we save the number of the frames
        Runner.size_arr1 = index_1 - 1
        #we sort each array individually
        Runner.arr1 = sorted(Runner.arr1)
        Runner.arr2 = sorted(Runner.arr2)
        Runner.arr3 = sorted(Runner.arr3)
        Runner.arr4 = sorted(Runner.arr4)
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--cal', action='store_true', dest='cal',
                        help='Execute calibration')

    parser.add_argument('--rtrec', action='store_true', dest='rtrec',
                        help='Execute real time recording')

    parser.add_argument('--outputsh', action='store_true',dest='outputsh',
                        help='Output recording show')

    parser.add_argument('--save', action='store_true',dest='save',
                        help='Output recording show')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    results = parser.parse_args()

    if results.cal == True:     #Here we run the calibration function
        CamRGBenv.gui_calibration()
    if results.rtrec == True:   #Here we run the real-time function
        CamRGBenv.gui_rt_rec()
    if results.outputsh == True:    #Here we run the output-show function
        CamRGBenv.gui_output_show()
    if results.save == True:
        CamRGBenv.gui_save_output()



