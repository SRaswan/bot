import rclpy
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist

# Creating a class for the echo camera node. Note that this class inherits from the Node class.
class echo_camera(Node):
	def __init__(self):
		#Initializing a node with the name 'echo_camera'
		super().__init__('echo_camera')
		
		#Subscribing to the /oak/rgb/image_raw topic that carries data of Image type
		self.subscription = self.create_subscription(Image, '/oak/rgb/image_raw', self.echo_topic, 10)
		self.publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
		self.subscription #this is just to remove unused variable warnings
		
		#CvBridge has functions that allow you to convert ROS Image type data into OpenCV images
		self.br = CvBridge()

                
	# Callback function to echo the video frame being received	
	def echo_topic(self, data):
		msg = Twist()	
		
		#Logging a message - helps with debugging later on
		self.get_logger().info('Receiving video frame')
		
		#Using the CvBridge function imgmsg_to_cv to convert ROS Image to OpenCV image
		current_frame = self.br.imgmsg_to_cv2(data)
		hsv = cv2.cvtColor(current_frame, cv2.COLOR_BGR2HSV)

		#HSV
		blue_mask = cv2.inRange(hsv, (55, 50, 50), (130, 255, 255))
		red_mask = cv2.inRange(hsv, (160, 50, 50), (180, 255, 255))
		green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))

		#Current frame masked with the hsv thresholds so we can isolate colors
		blue_masked_frame = cv2.bitwise_and(current_frame, current_frame, mask=blue_mask)
		red_masked_frame = cv2.bitwise_and(current_frame, current_frame, mask=red_mask)
		green_masked_frame = cv2.bitwise_and(current_frame, current_frame, mask=green_mask)


		#If blue showing at all, we keep moving in a circle
		if blue_masked_frame.any() > 0:
			msg.linear.x = 2.0
			msg.angular.z = 1.8
		#If red showing when blue not showing at all, we stop (we can also count and compare pixel values of red and blue if we want to in the future)
		elif red_masked_frame.any() > 0:
			msg.linear.x = 0.0
			msg.angular.z = 0.0
		#Using the imshow function to echo display the image frame currrently being published by the OAK-D
		cv2.imshow("color detected", np.hstack([current_frame, blue_masked_frame, red_masked_frame]))

		#This shows each image frame for 1 millisecond
		cv2.waitKey(1)
		self.publisher_.publish(msg)

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