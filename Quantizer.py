import numpy as np,math
from Utils import LogBuilder

""" Class responsibility is about image quantization algorithm and data structure managing """
class Quantizer():
    MUL_FACTOR = 28
    ROTATE_FACTOR = 0.2
    logger = LogBuilder(__name__, False)

    def __init__(self,my_orients,people_around_orients):
        Quantizer.logger.info(" %%%%%%%%%% QUANTIZATION START %%%%%%%%%% ")
        # x axis
        self.__basic_step_size = 0.5
        self.__x_quant = list(np.arange(-90, 90.5, self.__basic_step_size))
        Quantizer.logger.info("X-AXIS quantization bins are = (-90,90)")
        self.__my_tag = my_orients["tag"]
        Quantizer.logger.info("My tag is = " + str(self.__my_tag))
        self.__my_x_face_ratio = my_orients["x_ratio"]
        Quantizer.logger.info("My face orientation in X-AXIS from left edge is = " + str(self.__my_x_face_ratio))
        self.__my_x_bin_number = math.floor(float(self.__my_x_face_ratio) * (len(self.__x_quant) - 1))
        self.__my_x_bin_quant = self.__x_quant[self.__my_x_bin_number]
        Quantizer.logger.info("My X-AXIS quantize value is = " + str(self.__my_x_bin_quant))
        Quantizer.logger.info("My X-AXIS bin number is = " + str(self.__my_x_bin_number))
        self.__people_x_bins_orients = {}
        for key in people_around_orients:
            self.__people_x_perc = people_around_orients[key]["x_ratio"]
            self.__people_x_bins_orients[key] = self.__x_quant[math.floor(float(self.__people_x_perc) * (len(self.__x_quant) - 1))]
        Quantizer.logger.info("People around X-AXIS quantization = " + str(self.__people_x_bins_orients))
        # y_axis
        self.__people_y_bins_orients = {}
        self.__my_y_face_ratio = my_orients["y_ratio"]
        for key in people_around_orients:
            self.__people_y_bins_orients[key] = people_around_orients[key]["y_ratio"]
        Quantizer.logger.info("People around Y-AXIS = " + str(self.__people_y_bins_orients))
        Quantizer.logger.info(" %%%%%%%%%% QUANTIZATION END %%%%%%%%%% ")


    def get_gap_factor(self):
        return self.__basic_step_size*Quantizer.MUL_FACTOR


    def get_x_orient_value(self,index):
        return self.__x_quant[math.floor(index)]

    def get_x_quant_size(self):
        return len(self.__x_quant) - 1


    def get_my_quant(self):
        return {"x_ratio":self.__my_x_bin_quant,"y_ratio":self.__my_y_face_ratio}    # {x axis,y axis}


    def get_people_around_quant(self):
        return {"x_ratio":self.__people_x_bins_orients,"y_ratio":self.__people_y_bins_orients}    # {x axis}


    def update_my_quant(self,my_orients):
        # x axis
        self.__my_x_face_ratio = my_orients["x_ratio"]
        self.__my_x_bin_number = math.floor(float(self.__my_x_face_ratio) * (len(self.__x_quant) - 1))
        self.__my_x_bin_quant = self.__x_quant[self.__my_x_bin_number]
        Quantizer.logger.info("My new X-AXIS quantize value is = " + str(self.__my_x_bin_quant))
        Quantizer.logger.info("My new X-AXIS bin number is = " + str(self.__my_x_bin_number))
        # y axis
        self.__my_y_face_ratio = my_orients["y_ratio"]


    def update_people_around_quant(self,people_around_orients):
        # x axis
        self.__people_x_bins_orients = self.__people_y_bins_orients = {}
        for key in people_around_orients:
            self.__people_x_perc = people_around_orients[key]["x_ratio"]
            self.__people_x_bins_orients[key] = self.__x_quant[math.floor(float(self.__people_x_perc) * (len(self.__x_quant) - 1))]
            self.__people_y_bins_orients[key] = people_around_orients[key]["y_ratio"]
        Quantizer.logger.info("People around new X-AXIS quantization = " + str(self.__people_x_bins_orients))