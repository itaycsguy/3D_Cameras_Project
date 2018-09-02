from Quantizer import *
from Utils import *
from Calibrator import *
import cv2,shutil,time,csv
from Runner import *

class CamRGBenv():
    G_INVOKE_T = None
    G_INVOKE_D = None
    logger = LogBuilder(__name__, False)

    def __init__(self,me=None,**kwargs):
        if me is None or kwargs is None:
            raise Exception
        self.__my_img_tag = me[0]
        self.__my_img_name = me[1]
        self.__pose_detector = PoseDetector()
        self.__my_img_orients = self.__reduce_to_orient_data(self.__pose_detector.get_face_keypoints(frame_name=self.__my_img_name),self.__my_img_tag)
        CamRGBenv.logger.info("My orientations is " + str(self.__my_img_orients))
        self.__calibrator = Calibrator(self.__pose_detector)
        self.__calibrator.make(**kwargs)
        self.__Quantizer = Quantizer(self.__my_img_orients,self.__calibrator.get_calibration())

    def __reduce_to_orient_data(self,data,tag):
        return {"x_ratio":data[0][0],"y_ratio":data[0][1],"tag":tag}


    def get_pose_detector(self):
        return self.__pose_detector


    def get_calibrator(self):
        return self.__calibrator


    def get_quantizer(self):
        return self.__Quantizer


    def __in_range(self,my_val,calib_val):
        return (my_val["y_ratio"] >= calib_val - Quantizer.ROTATE_FACTOR and my_val["y_ratio"] <= calib_val + Quantizer.ROTATE_FACTOR)


    def __in_range_of_x_axis(self,my_val,other_val):
        return (my_val >= (other_val - self.__Quantizer.get_gap_factor()) and my_val <= (other_val + self.__Quantizer.get_gap_factor()))



    def get_match(self,frame_name):
        frame_name = str(self.__my_img_tag) + "_" + str(frame_name) + ".jpg"
        me = self.__reduce_to_orient_data(self.__pose_detector.get_face_keypoints(frame_name=frame_name),self.__my_img_tag)
        me_x_axis = self.__Quantizer.get_x_orient_value(me["x_ratio"]*self.__Quantizer.get_x_quant_size())
        me_y_axis = self.__Quantizer.get_my_quant()
        # ["y_ratio"]
        people_around = self.__Quantizer.get_people_around_quant()
        match_hash = {}
        x_axis_items = people_around["x_ratio"]
        for key,value in x_axis_items.items():
            if self.__in_range_of_x_axis(me_x_axis,value):
                match_hash[key] = {"x_ratio":True,"y_ratio":False}
        y_ratio_items = people_around["y_ratio"]
        for key, value in y_ratio_items.items():
            if self.__in_range(me_y_axis,value):
                if key in match_hash.keys():
                    match_hash[key]["y_ratio"] = True
        match_arr = list()
        for key,_ in match_hash.items():
            if key in match_hash.keys():
                if match_hash[key]["x_ratio"] and match_hash[key]["y_ratio"]:
                    match_arr.append(key)
        if match_arr:
            return match_arr[0]
        return None


    """ Looking for corresponding files into input_files directory and computed_files directory. It cannot be missing some file for next step """
    @staticmethod
    def have_corresponding_files():
        files_counter = False
        for file in os.listdir(main_input_files_dir):
            if os.path.isfile(main_input_files_dir + "\\" + file) and True:
                c_file = None
                try:
                    c_file = file[:file.index(".jpg")] + "_keypoints.json"
                    if not os.path.exists(main_computed_files_dir + "\\" + c_file):
                        return False
                    else:
                        files_counter = True
                except Exception as _: pass
        if not files_counter:
            return False
        return True


    #Here we reset the date and time values
    #In case we want to do another recording
    @staticmethod
    def reset_date_and_time():
        CamRGBenv.G_INVOKE_T = None
        CamRGBenv.G_INVOKE_D = None


    #Here we get the current date and time
    @staticmethod
    def get_formatted_date_and_time():
        if not CamRGBenv.G_INVOKE_T or not CamRGBenv.G_INVOKE_D:
            CamRGBenv.G_INVOKE_T = time.strftime("%H_%M_%S")
            CamRGBenv.G_INVOKE_D = time.strftime("%d.%m.%Y")
        return  CamRGBenv.G_INVOKE_T + "_" + CamRGBenv.G_INVOKE_D


    @staticmethod
    def move_files_to_inner_directory(curr_dir):
        dir_name = curr_dir + "\\" + CamRGBenv.get_formatted_date_and_time()
        for file in os.listdir(curr_dir):
            file_path = curr_dir + "\\" + file
            if not os.path.isdir(file_path) and not file_path.endswith(".txt") and not file_path.endswith(".TXT") and not file_path.endswith(".zip") and not file_path.endswith(".7z"):
                if not os.path.exists(dir_name):
                    os.mkdir(dir_name)
                shutil.move(file_path,dir_name)


    @staticmethod
    def create_inner_fs(curr_dir,new_dir_name=None):
        if not new_dir_name:
            new_dir_name = CamRGBenv.get_formatted_date_and_time()
        dir_name = curr_dir + "\\" + new_dir_name
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        return dir_name



    # # In this function we save an video (.avi file)
    # # of the results in the "target_path"
    # @staticmethod
    # def write_avi_file(target_path=None, from_path=None):
    #     CamRGBenv.logger.info("Running into " + __name__ + ":write_avi_file")
    #     # parameters: target file name,method to save frames [uncompressed or -1 to pop up options,FPS,frame size
    #     if not target_path:
    #         target_path = main_dir + "\\output_files"
    #
    #     if not from_path:
    #         from_path = main_input_files_dir
    #
    #     from_dir_list = os.listdir(from_path)
    #     if not from_dir_list:   #if the directory is empty we raise exception
    #         raise Exception("Empty source directory")
    #
    #     fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #     video = cv2.VideoWriter(target_path + "\\video.avi", fourcc, 6.0, (640 * 2, 480 * 2))
    #     # Loop over frame from input_files
    #     for index in range(0, Runner.size_arr1 + 1):
    #         file = from_path + "\\" + str(index) + ".jpg"  # the frame name
    #         img = cv2.imread(file)
    #         if os.path.isfile(file):
    #             video.write(img)  # append each frame to the video
    #         index += 1
    #
    #     # Cleanup and save video
    #     cv2.destroyAllWindows()
    #     video.release()
    #     CamRGBenv.logger.info("The video is saved successfully!")


    @staticmethod
    def get_total_frames():
        total = 0
        for frame in os.listdir(main_input_files_dir):
            if not os.path.isdir(main_input_files_dir + "\\" + frame) and not frame.endswith(".txt") and not frame.endswith(".TXT") and not frame.endswith(".zip") and not frame.endswith(".7z"):
                total += 1
        return total


    # This Function saves the results:
    @staticmethod
    def gui_save_output():
        check = Runner.Get_Frames_Names()
        # if the input_file is empty then stop
        if check == -1:
            return

        inner_output_dir = CamRGBenv.create_inner_fs(main_dir + '\\output_files')
        inner_inner_output_dir = CamRGBenv.create_inner_fs(inner_output_dir, new_dir_name="Processed_Frames")
        csv_file = open(inner_output_dir + "\\Matches.csv", "w+")
        writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video = cv2.VideoWriter(inner_output_dir + "\\video.avi", fourcc, 6.0, (640 * 2, 480 * 2))


        Runner.arrange_data()
        #First we calculate the calibration photos
        camm1 = CamRGBenv(me=[1, "1_LookingStraight.jpg"], two="1_LookingAtPerson2.jpg", three="1_LookingAtPerson3.jpg",
                          four="1_LookingAtPerson4.jpg")
        camm2 = CamRGBenv(me=[2, "2_LookingStraight.jpg"], one="2_LookingAtPerson1.jpg", three="2_LookingAtPerson3.jpg",
                          four="2_LookingAtPerson4.jpg")
        camm3 = CamRGBenv(me=[3, "3_LookingStraight.jpg"], one="3_LookingAtPerson1.jpg", two="3_LookingAtPerson2.jpg",
                          four="3_LookingAtPerson4.jpg")
        camm4 = CamRGBenv(me=[4, "4_LookingStraight.jpg"], one="4_LookingAtPerson1.jpg", two="4_LookingAtPerson2.jpg",
                          three="4_LookingAtPerson3.jpg")

        total_frame = CamRGBenv.get_total_frames()
        CamRGBenv.logger.info("Running into " + __name__ + ":gui_save_output")
        #here we put output to the csv file
        writer.writerow([['Frame', 'P1_LookAt', 'P2_LookAt', 'P3_LookAt', 'P4_LookAt', 'GreenColor', 'RedColor']])
        indexP = 0
        while True:
            # print("Round " + str(indexP))
            NullKeyPoints = False
            #   The stop condition: if the frames has finished then stop
            if (Runner.arr1[indexP] == math.inf) or (Runner.arranged_arr2[indexP] == math.inf) or \
                    (Runner.arranged_arr3[indexP] == math.inf) or (Runner.arranged_arr4[indexP] == math.inf):  # stop condition
                CamRGBenv.logger.info("No more frames are left!")
                CamRGBenv.logger.info("The Loop Stopped at Frame " + str(indexP))
                break
            P1_LookAt = P2_LookAt = P3_LookAt = P4_LookAt = None
            F_Point1 = F_Point2 = F_Point3 = F_Point4 = None
            try:
                # here we get the face coordinates for each player
                F_Point1 = camm1.get_pose_detector().get_face_keypoints("1_" + str(Runner.arr1[indexP]))
                F_Point2 = camm2.get_pose_detector().get_face_keypoints("2_" + str(Runner.arranged_arr2[indexP]))
                F_Point3 = camm3.get_pose_detector().get_face_keypoints("3_" + str(Runner.arranged_arr3[indexP]))
                F_Point4 = camm4.get_pose_detector().get_face_keypoints("4_" + str(Runner.arranged_arr4[indexP]))

                # We check wether eack person is looking at
                P1_LookAt = camm1.get_match(Runner.arr1[indexP])  # get the number of the player that matched player 1
                P2_LookAt = camm2.get_match(Runner.arranged_arr2[indexP])  # get the number of the player that matched player 2
                P3_LookAt = camm3.get_match(Runner.arranged_arr3[indexP])  # get the number of the player that matched player 3
                P4_LookAt = camm4.get_match(Runner.arranged_arr4[indexP])  # get the number of the player that matched player 4

            except Exception as ex:  # print the exception if it exist
                NullKeyPoints = True
                CamRGBenv.logger.info("Cannot detect image points")

            # now we read the images for each player from the suitable file
            img1 = cv2.imread(main_input_files_dir + '\\1_' + str(Runner.arr1[indexP]) + ".jpg")
            img2 = cv2.imread(main_input_files_dir + '\\2_' + str(Runner.arranged_arr2[indexP]) + ".jpg")
            img3 = cv2.imread(main_input_files_dir + '\\3_' + str(Runner.arranged_arr3[indexP]) + ".jpg")
            img4 = cv2.imread(main_input_files_dir + '\\4_' + str(Runner.arranged_arr4[indexP]) + ".jpg")



            Green_match = RED_match = '-'
            if NullKeyPoints == False:
                # here we define the rectangle coordinates
                # in order to mark the player with rectangle around his face
                UpperCoor1 = (int(F_Point1[1][1][0]) - 10, int(F_Point1[1][1][1]) - 100)  # (x=,y=)U
                ButtomCoor1 = (int(F_Point1[1][2][0]) + 10, int(F_Point1[1][2][1]) + 100)
                UpperCoor2 = (int(F_Point2[1][1][0]) - 10, int(F_Point2[1][1][1]) - 100)
                ButtomCoor2 = (int(F_Point2[1][2][0]) + 10, int(F_Point2[1][2][1]) + 100)
                UpperCoor3 = (int(F_Point3[1][1][0]) - 10, int(F_Point3[1][1][1]) - 100)
                ButtomCoor3 = (int(F_Point3[1][2][0]) + 10, int(F_Point3[1][2][1]) + 100)
                UpperCoor4 = (int(F_Point4[1][1][0]) - 10, int(F_Point4[1][1][1]) - 100)
                ButtomCoor4 = (int(F_Point4[1][2][0]) + 10, int(F_Point4[1][2][1]) + 100)
                line_width = 3
                green = (0, 255, 0)
                red = (0, 0, 255)

                # check for each two players if there is a communication between them
                if ((P1_LookAt == 2) & (P2_LookAt == 1)):
                    RED_match = '1 <-> 2'
                    cv2.rectangle(img1, UpperCoor1, ButtomCoor1, red, line_width)  # mark the suitable player's faces
                    cv2.rectangle(img2, UpperCoor2, ButtomCoor2, red, line_width)
                if ((P1_LookAt == 3) & (P3_LookAt == 1)):
                    RED_match = '1 <-> 3'
                    cv2.rectangle(img1, UpperCoor1, ButtomCoor1, red, line_width)  # mark the suitable player's faces
                    cv2.rectangle(img3, UpperCoor3, ButtomCoor3, red, line_width)
                if ((P1_LookAt == 4) & (P4_LookAt == 1)):
                    RED_match = '1 <-> 4'
                    cv2.rectangle(img1, UpperCoor1, ButtomCoor1, red, line_width)  # mark the suitable player's faces
                    cv2.rectangle(img4, UpperCoor4, ButtomCoor4, red, line_width)
                if ((P2_LookAt == 3) & (P3_LookAt == 2)):
                    Green_match = '2 <-> 3'
                    cv2.rectangle(img3, UpperCoor3, ButtomCoor3, green, line_width)  # mark the suitable player's faces
                    cv2.rectangle(img2, UpperCoor2, ButtomCoor2, green, line_width)
                if ((P2_LookAt == 4) & (P4_LookAt == 2)):
                    Green_match = '2 <-> 4'
                    cv2.rectangle(img4, UpperCoor4, ButtomCoor4, green, line_width)  # mark the suitable player's faces
                    cv2.rectangle(img2, UpperCoor2, ButtomCoor2, green, line_width)
                if ((P3_LookAt == 4) & (P4_LookAt == 3)):
                    Green_match = '3 <-> 4'
                    cv2.rectangle(img3, UpperCoor3, ButtomCoor3, green, line_width)  # mark the suitable player's faces
                    cv2.rectangle(img4, UpperCoor4, ButtomCoor4, green, line_width)

            if P1_LookAt == None:
                P1_LookAt = '-'
            if P2_LookAt == None:
                P2_LookAt = '-'
            if P3_LookAt == None:
                P3_LookAt = '-'
            if P4_LookAt == None:
                P4_LookAt = '-'

            # print for each player at who he is looking
            # filewriter.writerow(['', RED_match, Green_match, P4_LookAt, P3_LookAt, P2_LookAt, P1_LookAt, indexP])
            writer.writerow([indexP, P1_LookAt, P2_LookAt, P3_LookAt, P4_LookAt, Green_match, RED_match])

            # Here we merge all the images together in one window
            numpy_vertical_concat1 = np.concatenate((img1, img2), axis=0)
            numpy_vertical_concat2 = np.concatenate((img3, img4), axis=0)
            numpy_horizontal_concat = np.concatenate((numpy_vertical_concat1, numpy_vertical_concat2), axis=1)


            cv2.imwrite(os.path.join(inner_inner_output_dir, str(indexP) + ".jpg"), numpy_horizontal_concat)
            video.write(numpy_horizontal_concat)  # append each frame to the video

            # here we advance the pointer for the next frame
            indexP += 1

            try:
                print("Frame #{} of {}".format(indexP,total_frame/4))
            except Exception as _: pass

        cv2.destroyAllWindows()



        # Cleanup and save video
        video.release()

        csv_file.close()
        CamRGBenv.logger.info("The data have written to a csv file successfully!")
        #Update the data and save the frames in inner directory and json files
        CamRGBenv.move_files_to_inner_directory(main_dir + '\\computed_files')
        CamRGBenv.move_files_to_inner_directory(main_input_files_dir)
        CamRGBenv.reset_date_and_time()
        return inner_inner_output_dir


    # This Function outputs the results:
    # show interaction between the players (if exist)
    @staticmethod
    def gui_output_show():
        CamRGBenv.logger.info("Running into " + __name__ + ":gui_output_show")
        inner_inner_output_dir = CamRGBenv.gui_save_output()
        #Here we display the results
        for i in range(0, Runner.size_arr1 + 1):
            OutputIm = cv2.imread(inner_inner_output_dir + "\\" + str(i) + ".jpg")
            cv2.imshow('Results', cv2.resize(OutputIm, Runner.AllImSize,interpolation=cv2.INTER_CUBIC))  # parameeter one: 'numpy_horizontal_concat'
            k = cv2.waitKey(100)
            if k % 256 == 27:  # ESC pressed
                break
            i += 1
        cv2.destroyAllWindows()



    # This Function take the calibration frames for each player
    # and saves them in the input_files directory
    @staticmethod
    def gui_calibration():
        CamRGBenv.logger.info("Running into " + __name__ + ":gui_calibration")
        while True:  # initializing person 1
            s, im = Runner.cam1.read()  # read frame
            if not s:  # if it fails then we exit
                break
            cv2.imshow("initializing person 1", im)
            k = cv2.waitKey(1)
            if k % 256 == 27:  # ESC pressed
                CamRGBenv.logger.info("Escape is pressed, go to the second player")
                break
            elif k % 256 == 50:  # Number two pressed
                cv2.imwrite(main_input_files_dir + '\\1_LookingAtPerson2.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 51:  # Number three pressed
                cv2.imwrite(main_input_files_dir + '\\1_LookingAtPerson3.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 52:  # Number four pressed
                cv2.imwrite(main_input_files_dir + '\\1_LookingAtPerson4.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 53:  # Number five pressed
                cv2.imwrite(main_input_files_dir + '\\1_LookingStraight.jpg', im)
                cv2.waitKey(2000)

        cv2.destroyWindow('initializing person 1')

        while True:  # initializing person 2
            s, im = Runner.cam2.read()  # read frame
            if not s:  # if it fails then we exit
                break
            cv2.imshow("initializing person 2", im)  # show currnet image in real-time
            k = cv2.waitKey(1)
            if k % 256 == 27:  # ESC pressed
                CamRGBenv.logger.info("Escape is pressed, go to the third player")
                break
            elif k % 256 == 49:  # Number one pressed
                cv2.imwrite(main_input_files_dir + '\\2_LookingAtPerson1.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 51:  # Number three pressed
                cv2.imwrite(main_input_files_dir + '\\2_LookingAtPerson3.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 52:  # Number four pressed
                cv2.imwrite(main_input_files_dir + '\\2_LookingAtPerson4.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 53:  # Number five pressed
                cv2.imwrite(main_input_files_dir + '\\2_LookingStraight.jpg', im)
                cv2.waitKey(2000)

        cv2.destroyWindow('initializing person 2')

        while True:  # initializing person 3
            s, im = Runner.cam3.read()  # read frame
            if not s:  # if it fails then we exit
                break
            cv2.imshow("initializing person 3", im)  # show current frame in real-time
            k = cv2.waitKey(1)
            if k % 256 == 27:  # ESC pressed
                CamRGBenv.logger.info("Escape is pressed, go to the fourth player")
                break
            elif k % 256 == 49:  # Number one pressed
                cv2.imwrite(main_input_files_dir + '\\3_LookingAtPerson1.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 50:  # Number two pressed
                cv2.imwrite(main_input_files_dir + '\\3_LookingAtPerson2.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 52:  # Number four pressed
                cv2.imwrite(main_input_files_dir + '\\3_LookingAtPerson4.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 53:  # Number five pressed
                cv2.imwrite(main_input_files_dir + '\\3_LookingStraight.jpg', im)
                cv2.waitKey(2000)

        cv2.destroyWindow('initializing person 3')

        while True:  # initializing person 4
            s, im = Runner.cam4.read()  # read frame
            if not s:  # if it fails then we exit
                break
            cv2.imshow("initializing person 4", im)
            k = cv2.waitKey(1)
            if k % 256 == 27:  # ESC pressed
                CamRGBenv.logger.info("Escape is pressed, the calibration is saved successfully!")
                break
            elif k % 256 == 49:  # Number one pressed
                cv2.imwrite(main_input_files_dir + '\\4_LookingAtPerson1.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 50:  # Number two pressed
                cv2.imwrite(main_input_files_dir + '\\4_LookingAtPerson2.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 51:  # Number three pressed
                cv2.imwrite(main_input_files_dir + '\\4_LookingAtPerson3.jpg', im)
                cv2.waitKey(2000)
            elif k % 256 == 53:  # Number five pressed
                cv2.imwrite(main_input_files_dir + '\\4_LookingStraight.jpg', im)
                cv2.waitKey(2000)

        cv2.destroyWindow('initializing person 4')


    # Here we start recording each player
    # and save the frames in the input_files directory
    @staticmethod
    def gui_rt_rec():
        CamRGBenv.logger.info("Running into " + __name__ + ":gui_rt_rec")
        # Now we are going to step two
        # get the input frames and save them in the suitable folder
        while True:
            # read frame for each player
            s1, im1 = Runner.cam1.read()
            s2, im2 = Runner.cam2.read()
            s3, im3 = Runner.cam3.read()
            s4, im4 = Runner.cam4.read()

            if s1:  # if person one exist
                cv2.putText(im1, "Person #1", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0),2)  # add the person's name to the current frame
                FrameTime = time.clock()
                cv2.imwrite(main_input_files_dir + '\\1_' + str(FrameTime) + '.jpg', im1)  # save the frame
            if s2:
                cv2.putText(im2, "Person #2", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                numpy_vertical_concat1 = np.concatenate((im1, im2), axis=0)
                FrameTime = time.clock()
                cv2.imwrite(main_input_files_dir + '\\2_' + str(FrameTime) + '.jpg', im2)
            if s3:
                cv2.putText(im3, "Person #3", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                FrameTime = time.clock()
                cv2.imwrite(main_input_files_dir + '\\3_' + str(FrameTime) + '.jpg',im3)
            if s4:
                cv2.putText(im4, "Person #4", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                numpy_vertical_concat2 = np.concatenate((im3, im4), axis=0)
                numpy_horizontal_concat = np.concatenate((numpy_vertical_concat1, numpy_vertical_concat2), axis=1)
                FrameTime = time.clock()
                cv2.imwrite(main_input_files_dir + '\\4_' + str(FrameTime) + '.jpg',im4)
            if not s2:
                cv2.imshow('Input Channel', cv2.resize(im1, Runner.AllImSize, interpolation=cv2.INTER_CUBIC))
                cv2.waitKey(1)
            elif not s3:
                cv2.imshow('Input Channel',cv2.resize(numpy_vertical_concat1, Runner.AllImSize, interpolation=cv2.INTER_CUBIC))
                cv2.waitKey(1)
            elif not s4:
                numpy_vertical_concat2 = np.concatenate((im3, im3), axis=0)
                numpy_horizontal_concat = np.concatenate((numpy_vertical_concat1, numpy_vertical_concat2), axis=1)
                cv2.imshow('Input Channel',cv2.resize(numpy_horizontal_concat, Runner.AllImSize, interpolation=cv2.INTER_CUBIC))
            else:
                cv2.imshow('Input Channel',cv2.resize(numpy_horizontal_concat, Runner.AllImSize, interpolation=cv2.INTER_CUBIC))

            k = cv2.waitKey(1)
            # the stop condition
            # if ESC is pressed we exit
            if k % 256 == 27:  # ESC pressed
                CamRGBenv.logger.info("The recording is finished successfully!")
                break

        cv2.destroyWindow('Input Channel')
