from tkinter import *
from CamRGBenv import *
from Utils import *

class GCam():
    MAIN_BUTTONS_SIZE = 40
    MAIN_BUTTONS_LINE_NUMBER = 3

    CANVAS_WIDTH = 200
    CANVAS_HEIGHT = 200

    CANVAS_IMG_WIDTH = 100
    CANVAS_IMG_HEIGHT = 10

    APP_TITLE = "Pair Interaction Detector"

    ### MENU ###
    RESET_TEXT = "Reset"
    EXIT_TEXT = "Exit"
    OPTIONS_TEXT = "Options"
    ABOUT_TEXT = "About..."
    HELP_TEXT = "Help"
    ############

    ### ACTIONS ###
    CALIBRATION_BUTTON_TEXT = "Start Calibration"
    RT_VIDEO_BUTTON_TEXT = "Start RT Recording"
    OUTPUT_BUTTON_TEXT = "Show And Save Output Video"
    SAVE_OUTPUT_BUTTON_TEXT = "Save Output Video"
    ###############

    ### ABOUT ###
    ABOUT_TITLE = "About..."
    ABOUT_GEO = "250x100"
    ABOUT_TEXT_VIEW = "Developers: Itay Guy And Elias Jadon\nInstitute: University Of Haifa\nInstructor: Prof. Hel-Or Hagit\nCourse: 3D-Cameras"
    #############

    ### OUTPUT SHOW ###
    OUTPUT_ERR_GRO = "350x100"
    FILES_NOT_EXIST = "Not Exist Files Error"
    FILES_NOT_EXIST_ERROR = "Put files into \"input_files\" and \"computed_files\"\nOR\nDo a Calibration and RT Recording NOW to a group meeting"


    @staticmethod
    def is_env_var_declared():
        if os.environ['APP_PATH'] and os.environ['INPUT_FILES'] and os.environ['COMPUTED_FILES']:
            return True
        return False


    def __init__(self):
        self.step_flags = {"env_var":GCam.is_env_var_declared(),"calibration":False,"rt_video":False}
        self.root = Tk()
        self.root.title(GCam.APP_TITLE)
        self.root.resizable(0,0)
        self.init_components()

    def init_components(self):
        menubar = Menu(self.root)
        ordered_buttons = [self.get_calibration_button(),self.get_rt_record_button(),self.get_output_button(),self.get_save_output_button()]
        self.config_main_buttons_layout(ordered_buttons)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label=GCam.RESET_TEXT, command=self.reset)
        filemenu.add_separator()
        filemenu.add_command(label=GCam.EXIT_TEXT, command=self.root.destroy)
        menubar.add_cascade(label=GCam.OPTIONS_TEXT, menu=filemenu)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label=GCam.ABOUT_TEXT, command=self.about)
        menubar.add_cascade(label=GCam.HELP_TEXT, menu=helpmenu)
        self.root.config(menu=menubar)
        img = PhotoImage(file=IMG_LOGO)
        canvas = Canvas(self.root, width=GCam.CANVAS_WIDTH, height=GCam.CANVAS_HEIGHT)
        canvas.pack(side=TOP)
        canvas.create_image(GCam.CANVAS_IMG_WIDTH, GCam.CANVAS_IMG_HEIGHT, anchor=N ,image=img)
        self.root.mainloop()


    def are_conditions_satisfied(self):
        for _,value in self.step_flags.items():
            if not value:
                return False
        return True


    def compute_key_points(self,event):
        self.root.update_idletasks()
        if not self.are_conditions_satisfied():
            self.root.title("Incomplete Pre-conditions!")
            time.sleep(1)
        else:
            PoseDetector.perform()
            self.root.update_idletasks()
            time.sleep(1)
        self.root.update_idletasks()
        self.root.title(GCam.APP_TITLE)


    def get_rt_record_button(self):
        button = Button(self.root, text=GCam.RT_VIDEO_BUTTON_TEXT,cursor="hand2")
        button.bind('<Button-1>',self.start_rt_video_record)
        return button

    def get_calibration_button(self):
        button = Button(self.root, text=GCam.CALIBRATION_BUTTON_TEXT,cursor="hand2")
        button.bind('<Button-1>',self.start_calibration)
        return button

    def get_output_button(self):
        button = Button(self.root, text=GCam.OUTPUT_BUTTON_TEXT,cursor="hand2")
        button.bind('<Button-1>', self.show_output_video)
        return button

    def get_save_output_button(self):
        button = Button(self.root, text=GCam.SAVE_OUTPUT_BUTTON_TEXT,cursor="hand2")
        button.bind('<Button-1>', self.save_output_video)
        return button



    def config_main_buttons_layout(self,ordered_buttons):
        for idx,button in enumerate(ordered_buttons):
            button.config(width=GCam.MAIN_BUTTONS_SIZE,padx=5,pady=5,bd=3)
            button.pack()

    def start(self):
        self.root.mainloop()


    def start_calibration(self,event):
        self.root.update_idletasks()
        self.root.title("Running Calibration...")
        CamRGBenv.gui_calibration()
        self.root.update_idletasks()
        self.root.title("Completed!")
        time.sleep(1)
        self.root.update_idletasks()
        self.root.title(GCam.APP_TITLE)
        self.step_flags["calibration"] = True
        if self.are_conditions_satisfied():
            self.compute_key_points(event)


    def start_rt_video_record(self,event):
        self.root.update_idletasks()
        self.root.title("Running Video Record...")
        CamRGBenv.gui_rt_rec()
        self.root.update_idletasks()
        self.root.title("Saved!")
        time.sleep(1)
        self.root.update_idletasks()
        self.root.title(GCam.APP_TITLE)
        self.step_flags["rt_video"] = True
        if self.are_conditions_satisfied():
            self.compute_key_points(event)


    def show_output_video(self,event):
        if not CamRGBenv.have_corresponding_files():
            top = Toplevel(self.root)
            top.geometry(GCam.OUTPUT_ERR_GRO)
            top.title(GCam.FILES_NOT_EXIST)
            label = Label(top, text=GCam.FILES_NOT_EXIST_ERROR, font=("Helvetica", 9, "bold"), relief="flat")
            label.pack(side=TOP, pady=1, padx=1)
            button = Button(top,text="Ok",font=("Helvetica", 10, "bold"), relief="raised",cursor="hand2",command=top.destroy)
            button.pack(side=BOTTOM,pady=5, padx=1)
            return
        self.root.update_idletasks()
        self.root.title("Running And Saving Output Video...")
        CamRGBenv.gui_output_show()
        self.root.update_idletasks()
        self.root.title("Finished!")
        time.sleep(1)
        self.root.update_idletasks()
        self.root.title(GCam.APP_TITLE)
        self.reset()



    def save_output_video(self,event):
        if not CamRGBenv.have_corresponding_files():
            top = Toplevel(self.root)
            top.geometry(GCam.OUTPUT_ERR_GRO)
            top.title(GCam.FILES_NOT_EXIST)
            label = Label(top, text=GCam.FILES_NOT_EXIST_ERROR, font=("Helvetica", 9, "bold"), relief="flat")
            label.pack(side=TOP, pady=1, padx=1)
            button = Button(top,text="Ok",font=("Helvetica", 10, "bold"), relief="raised",cursor="hand2",command=top.destroy)
            button.pack(side=BOTTOM,pady=5, padx=1)
            return
        self.root.update_idletasks()
        self.root.title("Saving Output Video...")
        CamRGBenv.gui_save_output()
        self.root.update_idletasks()
        self.root.title("Finished!")
        time.sleep(1)
        self.root.update_idletasks()
        self.root.title(GCam.APP_TITLE)
        self.reset()



    def reset(self):
        self.root.update_idletasks()
        self.root.title("Make Reset...")
        self.step_flags = {"env_var":GCam.is_env_var_declared(),"calibration":False,"rt_video":False}
        self.root.update_idletasks()
        self.root.title("Finished And Ready!")
        time.sleep(1)
        self.root.update_idletasks()
        self.root.title(GCam.APP_TITLE)


    def about(self):
        top = Toplevel(self.root)
        top.geometry(GCam.ABOUT_GEO)
        top.title(GCam.ABOUT_TITLE)
        label = Label(top,text=GCam.ABOUT_TEXT_VIEW,font=("Helvetica", 10,"bold"),relief="groove")
        label.pack(side=TOP,pady=1, padx=1)
        button = Button(top, text="Close", font=("Helvetica", 10, "bold"), relief="raised", cursor="hand2",command=top.destroy)
        button.pack(side=BOTTOM, pady=5, padx=1)



if __name__ == "__main__":
    GCam().start()
