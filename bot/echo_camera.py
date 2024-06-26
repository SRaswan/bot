import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

# Creating a class for the echo camera node. Note that this class inherits from the Node class.
class echo_camera(Node):
	def __init__(self):
		#Initializing a node with the name 'echo_camera'
		super().__init__('echo_camera')
		
		#Subscribing to the /oak/rgb/image_raw topic that carries data of Image type
		self.subscription = self.create_subscription(Image, '/oak/rgb/image_raw', self.echo_topic, 10)
		self.subscription #this is just to remove unused variable warnings
		
		#CvBridge has functions that allow you to convert ROS Image type data into OpenCV images
		self.br = CvBridge()
	
	# Callback function to echo the video frame being received	
	def echo_topic(self, data):
		#Logging a message - helps with debugging later on
		self.get_logger().info('Receiving video frame')
		
		#Using the CvBridge function imgmsg_to_cv to convert ROS Image to OpenCV image. Now you can use this image to do other OpenCV things
		current_frame = self.br.imgmsg_to_cv2(data)
		
		#Using the imshow function to echo display the image frame currrently being published by the OAK-D
		cv2.imshow("camera", current_frame)

		#This shows each image frame for 1 millisecond, try playing around with different wait values to achieve the video framerate you want!
		cv2.waitKey(1)

# Main function 		
def main(args=None):
	# Initializing rclpy (ROS Client Library for Python)
	rclpy.init(args=args)
	
	#Create an object of the echo_camera class
	echo_obj = echo_camera()
	
	#Keep going till termination
	rclpy.spin(echo_obj)
	
	#Destroy node when done 
	echo_obj.destroy_node()
	
	#Shutdown rclpy
	rclpy.shutdown()
	
if __name__ == '__main__':
	main()