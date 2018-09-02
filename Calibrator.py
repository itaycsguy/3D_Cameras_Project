from Utils import *

"""
This class responsibility is about the calibration time before workflow is started.
This is happening once in execution time and being as an anchor the the execution correctness and success
"""
class Calibrator():
    logger = LogBuilder(__name__, False)

    def __init__(self,pose_detector,debug_mode=False):
        Calibrator.logger.setLevel(debug_mode)
        self.__pose_detector = pose_detector
        self.__radian2degrees = 57.2957795 # known parameter
        self.__calib_hash = list()


    def __dotproduct(self,v1, v2):
        return sum((a * b) for a, b in zip(v1, v2))


    def __length(self,v):
        return math.sqrt(self.__dotproduct(v, v))


    def angle(self,v1, v2):
        return math.acos(self.__dotproduct(v1, v2) / (self.__length(v1) * self.__length(v2)))*self.__radian2degrees


    """
    get all calibration frame key points, than retrieve them keypoints and compute angles between the anchor frame one ['my_img']
    ***keep the calibration array and static class array
    """
    def make(self,**kwargs):
        Calibrator.logger.debug(" %%%%%%%%%% CALIBRATION START %%%%%%%%%% ")
        if self.__pose_detector is None or kwargs is None:
            return None
        self.__calib_hash = {}
        for img_order in kwargs:
            state = self.__pose_detector.get_face_keypoints(frame_name=kwargs[img_order])
            Calibrator.logger.info("Metadata of People number " + str(img_order) + " = " + str(state))
            try:
                order = self.__get_tag(img_order)
                self.__calib_hash[order] = {"x_ratio":state[0][0],"y_ratio":state[0][1]}
            except Exception as _:
                return None
        Calibrator.logger.info("> People around hash points = " + str(self.__calib_hash))
        Calibrator.logger.debug(" %%%%%%%%%% CALIBRATION END %%%%%%%%%% ")
        return self.__calib_hash


    def get_calibration(self):
        return self.__calib_hash


    def __get_tag(self,tag_name):
        people_tag = None
        if tag_name == "one":
            people_tag = 1
        elif tag_name == "two":
            people_tag = 2
        elif tag_name == "three":
            people_tag = 3
        elif tag_name == "four":
            people_tag = 4
        if people_tag is None:
            raise Exception
        return people_tag