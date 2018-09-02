import os,json,sys,argparse,subprocess,logging,numpy as np
from Utils import LogBuilder

class PoseDetector():
	logger_counter = 0
	logger = LogBuilder(__name__,False)
	
	
	@staticmethod
	def audit(msg):
		if PoseDetector.logger_counter > 1:
			PoseDetector.logger.debug(msg)
		else:
			PoseDetector.logger.info(msg)
	
	
	def __init__(self,main_dir=None,debug_mode=False):
		if debug_mode:
			PoseDetector.logger.setLevel(logging.DEBUG)
		EDITTED_MAIN_DIR = False
		if not main_dir:
			main_dir = os.environ['APP_PATH']
			if not main_dir:
				PoseDetector.audit("Cannot executing without 'APP_PATH' environment variable definition.")
				sys.exit(-1)
		else:
			EDITTED_MAIN_DIR = True
		# PoseDetector.audit("PoseDetector:ENVIRONMENT VARIABLES FETCHING START")
		if not EDITTED_MAIN_DIR:
			self.__main_dir = main_dir
			# PoseDetector.audit("Main Dir Path =" + self.__main_dir)
			self.__main_input_files_dir = os.environ['INPUT_FILES']
			# PoseDetector.audit("Input Files Dir =" + self.__main_input_files_dir)
			self.__main_computed_files_dir = os.environ['COMPUTED_FILES']
			# PoseDetector.audit("Computed Files Dir =" + self.__main_computed_files_dir)
		else:
			self.__main_dir = main_dir
			# PoseDetector.audit("Main Dir Path =" + self.__main_dir)
			self.__main_input_files_dir = self.__main_dir + "\\input_files"
			# PoseDetector.audit("Input Files Dir =" + self.__main_input_files_dir)
			self.__main_computed_files_dir = self.__main_dir + "\\computed_files"
			# PoseDetector.audit("Computed Files Dir =" + self.__main_computed_files_dir)
		# PoseDetector.audit("PoseDetector:ENVIRONMENT VARIABLES FETCHING END")
		PoseDetector.logger_counter += 1
	

	def readFramePoints(self,frame_name=None):
		PoseDetector.logger.debug("PoseDetector:readFramePoints: READ FRAME POINTS START")
		if not frame_name:
			PoseDetector.logger.warning("PoseDetector:readFramePoints: No frame is attached.")
			return None
		content = list()
		for file in os.listdir(self.__main_computed_files_dir):
			file = file.strip()
			try:
				file_name = str(file[:file.index("_keypoints.json")]).strip()
				try:
					target_name = str(frame_name[:str(frame_name).index(".jpg")]).strip()
				except:
					target_name = str(frame_name).strip()
				if file_name == target_name:
					content = json.load(open(self.__main_computed_files_dir	+ "\\" + file,"r"))
					break
			except Exception as _:
				pass
		if content:
			face_items = list()
			max_x_len = 0
			for i in range(0,len(content['people'])):
				# pose_values = content['people'][i]['pose_keypoints'][:]
				face_values = content['people'][i]['face_keypoints'][:]
				left_face = face_values[0:3]
				right_face = face_values[16*3:16*3+3] 
				# under_nose = face_values[27*3:27*3+3]
				nose = face_values[33*3:33*3+3]	# pose_values[0:3] - worked well
				# jaw = face_values[8*3:8*3+3]
				x_len = abs(right_face[0] - left_face[0])
				if x_len > max_x_len:
					face_items = [nose,left_face,right_face]
					max_x_len = x_len
			if not face_items:
				return None
			PoseDetector.logger.debug("PoseDetector:readFramePoints: READ FRAME POINTS END")
			return face_items
		else:
			PoseDetector.logger.warning("PoseDetector:readFramePoints: Cannot detect any skeleton point.")
		return None


	def convertPercentageView(self,points):
		PoseDetector.logger.debug("PoseDetector:CONVERTION START")
		nose = left = right = nose_ratio = distance_triangle_ratio = 0.0
		nose = points[0][0]
		left = points[1][0]
		right = points[2][0]
		nose_ratio = abs(nose - left)/abs(right - left)
		if nose >= right:
			nose_ratio = 1.0
		elif nose <= left:
			nose_ratio = 0.0
		mid_sides_point = abs(np.subtract(points[2],points[1]))
		nose_height = abs(points[0] - mid_sides_point)
		nose_height = nose_height[1]
		distance_triangle_ratio = abs(right - left)/nose_height
		PoseDetector.logger.debug("PoseDetector:CONVERTION END")
		return [nose_ratio,distance_triangle_ratio]


	def detectFramePoints(self,frame_name=None,percentage_output=True):
		PoseDetector.logger.debug("PoseDetector:FRAME POINTS DETECTION START")
		if not frame_name:
			PoseDetector.logger.info("No frame is attached.")
			return None
		cmd =  self.__main_dir + 	"\\bin\\OpenPose.exe " + \
									" --face " + \
									" --no_display " + \
									" --image_dir " + self.__main_input_files_dir + \
									" --write_keypoint_json " + self.__main_computed_files_dir
		PoseDetector.logger.info("Command using OpenPose API Library: " + cmd)
		PoseDetector.logger.info("Computing skeleton points...")
		os.system(cmd)
		PoseDetector.logger.info("Completed!")
		if frame_name != "*":
			points = self.readFramePoints(frame_name)
			if not points:
				PoseDetector.logger.info("PoseDetector:detectFramePoints: No points are detected yet.")
				return None
			PoseDetector.logger.debug("PoseDetector:FRAME POINTS DETECTION END")
			if not percentage_output:
				return points
			return self.convertPercentageView(points)
			

	def get_face_keypoints(self,frame_name=None):
		if not frame_name:
			PoseDetector.logger.info("PoseDetector:get_face_keypoints: No frame is provided.")
			return None
		try:
			face_points = self.readFramePoints(frame_name=frame_name)
			if not face_points:
				PoseDetector.logger.info("PoseDetector:get_face_keypoints: Cannot detect face key-points.")
				return None
			else:
				# x axis
				face_points[0] = face_points[0][:2]
				face_points[1] = face_points[1][:2]
				face_points[2] = face_points[2][:2]
				computed_points = self.convertPercentageView(face_points)
				return [computed_points,face_points]
		except Exception as ex:
			raise ex
	
	
	@staticmethod
	def perform():
		pose_detector = PoseDetector()
		pose_detector.detectFramePoints(frame_name="*")

		
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--frame_name',nargs="?", dest='name',default=None,help='A frame name to work on')
	parser.add_argument('--path',nargs="?", dest='path',default=None,help='A full path to the .py modules')
	parser.add_argument('--action',nargs="?", dest='action',default="xw",help='\"xr\": face orientation location.\"r\":read a frame points.\"xw\":compute frames skeleton points [default].')
	parser.add_argument('--all',action="store_true", dest='all',default=False,help='compute the whole directory without any return value.')
	parser.add_argument('--debug',action="store_true", dest='debug',default=False,help='display messages as debug mode [default=False')
	parser.add_argument('--version', action='version', version='%(prog)s 1.0')
	results = parser.parse_args()
	debug_mode = results.debug
	path = None
	if results.path:
		path = results.path
	else:
		path = os.environ['APP_PATH']
	if results.name:
		pose_detector = PoseDetector(main_dir=path,debug_mode=debug_mode)
		try:
			if results.action == "r":
				ret_points = pose_detector.readFramePoints(frame_name=results.name)
				print(ret_points)
			elif results.action == "xr":
				ret_points = pose_detector.get_face_keypoints(frame_name=results.name)
				print(ret_points)
			elif results.action == "xw":
				ret_points = pose_detector.detectFramePoints(frame_name=results.name)
				print(ret_points)
			else:
				print("Wrong parameter\s!")
				sys.exit(-1)
		except Exception as ex:
			print("Frame is not exist/accessible.")
	elif results.all == True:
		pose_detector = PoseDetector(main_dir=path,debug_mode=debug_mode)
		pose_detector.detectFramePoints(frame_name="*")
	else:
		print("PoseDetector:get_face_keypoints:perform: No frame name is provided.")