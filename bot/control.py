# from pupper_interfaces.srv import GoPupper
# from MangDang.mini_pupper.display import Display, BehaviorState
# import rclpy
# from rclpy.node import Node
# import time
# import RPi.GPIO as GPIO
# import random
# import cv2
# from cv_bridge import CvBridge
# from resizeimage import resizeimage
# from PIL import Image as PILImage, ImageDraw, ImageFont
# from sensor_msgs.msg import Image

# RELATIVE = "/home/ubuntu/ros2_ws/src/bot/bot/img/"
# MOVES = ["move_forward", "move_right", "move_left"]
# COLORS = ["red", "green", "blue"]

# class SampleControllerAsync(Node):

#     def __init__(self):
#         super().__init__('sample_controller')
#         self.cli = self.create_client(GoPupper, 'pup_command')
		
#         self.subscription = None
#         self.current_frame = None
#         self.br = CvBridge()

#         while not self.cli.wait_for_service(timeout_sec=1.0):
#             self.get_logger().info('service not available, waiting again...')
        
#         self.req = GoPupper.Request()
#         self.sensor_stack = []
#         self.idx = 0
#         self.phase = 0
#         self.score = 0
#         self.timer = self.create_timer(1.0, self.pupper)

#     def send_move_request(self, idx):
#         self.req = GoPupper.Request()
#         self.req.command = MOVES[idx]
#         self.future = self.cli.call_async(self.req)
#         # rclpy.spin_until_future_complete(self, self.future)
#         return self.future.result()

#     def get_user_input(self):
#         tFront = GPIO.input(6)
#         tLeft = GPIO.input(3)
#         tRight = GPIO.input(16)
#         if not tFront:
#             return 0
#         elif not tRight:
#             return 1
#         elif not tLeft:
#             return 2
#         return -1

#     def cam(self, data):# Callback method to handle image data
#         try:
#             self.current_frame = self.br.imgmsg_to_cv2(data)# Convert ROS image message to OpenCV image
#         except Exception as e:
#             self.get_logger().error(f"Error converting image: {e}")

#     def pupper(self):
#         print("Phase ", self.phase)
#         # Phase 0: Choosing move
#         if self.phase == 0:
#             new_move = random.randint(0, 2)
#             self.sensor_stack.append(new_move)
#             print("Added move ", new_move)
#             self.phase = 1
#             self.idx = 0

#         # Phase 1: Choosing move
#         if self.phase == 1:
#             print("Dancing")
#             if self.idx < len(self.sensor_stack):
#                 self.send_move_request(self.sensor_stack[self.idx])
#                 self.idx += 1
#                 self.phase = 1
#             else:
#                 self.phase = 2
#                 self.idx = 0
    
#         # Phase 2: Sensing
#         if self.phase == 2:
#             print("Response")
#             response = self.get_user_input()
#             if response != -1:
#                 if response == self.sensor_stack[self.idx]:
#                     self.idx += 1
#                     self.score += 1
#                     self.display(MOVES[response]+".png")

#                     print("Nice! Keep going")
#                     if self.idx >= len(self.sensor_stack):
#                         print("Correct! Moving to the next level.")
#                         self.phase = 0
#                 else:
#                     print("You failed! Try again.")
#                     self.sensor_stack = []
#                     self.phase = 3

#         # Phase 3: Start cam
#         if self.phase == 3:
#             self.subscription = self.create_subscription(Image, '/oak/rgb/image_raw', self.cam, 10)
#             self.phase = 4

#         # Phase 4: Pick Color
#         if self.phase == 4:
#             print("Pick Color")
#             new_color = random.randint(0, 2)
#             self.sensor_stack.append(new_color)
#             print("Added color ", new_color)
#             self.phase = 5
#             self.idx = 0
        
#         # Phase 5: Show Color
#         if self.phase == 5:
#             print("Show Color")
#             if self.idx < len(self.sensor_stack):
#                 self.display(COLORS[self.sensor_stack[self.idx]]+".jpg")
#                 self.idx += 1
#             else:
#                 self.phase = 6
#                 self.idx = 0

#         # Phase 6: Viewing Colors
#         if self.phase == 6:
#             print("Response")
#             hsv = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2HSV)

#             blue_mask = cv2.inRange(hsv, (55, 50, 50), (130, 255, 255))
#             red_mask = cv2.inRange(hsv, (160, 50, 50), (180, 255, 255))
#             green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))

#             blue_masked_frame = cv2.bitwise_and(self.current_frame, self.current_frame, mask=blue_mask)
#             red_masked_frame = cv2.bitwise_and(self.current_frame, self.current_frame, mask=red_mask)
#             green_masked_frame = cv2.bitwise_and(self.current_frame, self.current_frame, mask=green_mask)       
#             cols = [blue_masked_frame, red_masked_frame, green_masked_frame]

#             if cv2.countNonZero(cols[self.sensor_stack[self.idx]]) > 15:
#                 self.idx += 1
#                 self.score += 1
#                 print("Nice! Keep going")
#                 if self.idx >= len(self.sensor_stack):
#                     print("Correct! Moving to the next level.")
#                     self.phase = 3
#             elif cv2.countNonZero(blue_masked_frame) > 15 or cv2.countNonZero(red_masked_frame) > 15 or cv2.countNonZero(green_masked_frame) > 15:
#                 print("You failed! Try again.")
#                 self.sensor_stack = []
#                 self.phase = 7

#         # Phase 7: Picture
#         if self.phase == 7:
#             print("Picture")
#             cv2.imwrite(RELATIVE+"pic.jpg", self.current_frame)
#             self.display("pic.jpg")
#             self.phase = 8


#     def display(self, pic):
#         impath = RELATIVE+pic
#         disp = Display()
#         print("Displaying: ", impath)

#         # try:
#         #     img = cv2.imread(impath)
#         #     if img is None:
#         #         raise FileNotFoundError("Image not found at path: ", impath)
#         #     img = cv2.resize(img, (320, 240))
#         #     cv2.imwrite(impath, img)
#         #     disp.show_image(impath)
#         # except Exception as e:
#         #     print("Error: ", e)

#         imgFile = PILImage.open(impath)
#         imgFile = resizeimage.resize_width(imgFile, 320)
#         imgFile.save(impath, imgFile.format)
#         disp.show_image(impath)
#         imgFile.close()


# def main():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(6, GPIO.IN)
#     GPIO.setup(3, GPIO.IN)
#     GPIO.setup(16, GPIO.IN)

#     rclpy.init()
#     sample_controller = SampleControllerAsync()

#     try:
#         rclpy.spin(sample_controller)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         sample_controller.destroy_node()
#         rclpy.shutdown()
#         GPIO.cleanup()

# if __name__ == '__main__':
#     main()



# VERSION 2

# from pupper_interfaces.srv import GoPupper  # Import the GoPupper service definition
# from MangDang.mini_pupper.display import Display, BehaviorState  # Import display and behavior state from mini_pupper
# import rclpy  # Import the ROS 2 Python client library
# from rclpy.node import Node  # Import Node class from ROS 2
# import time  # Import time module for delays
# import RPi.GPIO as GPIO  # Import GPIO library for Raspberry Pi GPIO pin control
# import random  # Import random module for random number generation
# import cv2  # Import OpenCV for image processing
# from cv_bridge import CvBridge  # Import CvBridge to convert ROS image messages to OpenCV images
# from PIL import Image as PILImage, ImageDraw, ImageFont  # Import PIL for image handling
# from sensor_msgs.msg import Image  # Import ROS Image message type

# RELATIVE = "/home/ubuntu/ros2_ws/src/bot/bot/img/"  # Define the relative path for images
# MOVES = ["move_forward", "move_right", "move_left"]  # List of possible movement commands
# COLORS = ["red", "green", "blue"]  # List of colors for display purposes

# class SampleControllerAsync(Node):  # Define the main class for the ROS node

#     def __init__(self):
#         super().__init__('sample_controller')  # Initialize the Node with the name 'sample_controller'
#         self.cli = self.create_client(GoPupper, 'pup_command')  # Create a client for the GoPupper service
        
#         self.subscription = None  # Initialize the subscription attribute
#         self.current_frame = None  # Initialize the current frame attribute
#         self.br = CvBridge()  # Initialize CvBridge for converting ROS images to OpenCV
#         self.disp = Display()  # Initialize the display

#         while not self.cli.wait_for_service(timeout_sec=1.0):  # Wait until the GoPupper service is available
#             self.get_logger().info('service not available, waiting again...')  # Log service unavailability
        
#         self.req = GoPupper.Request()  # Initialize the service request object
#         self.sensor_stack = []  # Initialize the list to store sensor stack
#         self.user_input_stack = []  # Initialize the list to store user inputs
#         self.idx = 0  # Initialize the index for tracking sensor stack
#         self.phase = 0  # Initialize the phase variable for game state management
#         self.score = 0  # Initialize the score variable
#         self.timer = self.create_timer(1.0, self.pupper)  # Create a timer to call the pupper method every second

#     def send_move_request(self, idx):  # Method to send movement requests
#         self.req = GoPupper.Request()  # Create a new request object
#         self.req.command = MOVES[idx]  # Set the command in the request object
#         self.future = self.cli.call_async(self.req)  # Call the service asynchronously
#         # rclpy.spin_until_future_complete(self, self.future)  # Wait until the service call is complete
#         return self.future.result()  # Return the result of the service call

#     def get_user_input(self):  # Method to get user input from GPIO
#         tFront = GPIO.input(6)  # Read front sensor
#         tLeft = GPIO.input(3)  # Read left sensor
#         tRight = GPIO.input(16)  # Read right sensor
#         if not tFront:
#             return 0  # Return 0 if front sensor is pressed
#         elif not tRight:
#             return 1  # Return 1 if right sensor is pressed
#         elif not tLeft:
#             return 2  # Return 2 if left sensor is pressed
#         return -1  # Return -1 if no sensor is pressed

#     def cam(self, data):  # Callback method to handle image data
#         try:
#             self.current_frame = self.br.imgmsg_to_cv2(data)  # Convert ROS image message to OpenCV image
#         except Exception as e:
#             self.get_logger().error(f"Error converting image: {e}")

#     def pupper(self):  # Main game logic method
#         self.display_phase_message()  # Display phase message on the screen
#         print("Phase ", self.phase)  # Print the current phase
#         if self.phase == 0:  # Phase 0: Choosing moves
#             new_move = random.randint(0, 2)  # Choose a random move
#             self.sensor_stack.append(new_move)  # Add the new move to the sensor stack
#             print(f"Added move {new_move}")  # Log the added move
#             self.phase = 1  # Move to phase 1
#             self.idx = 0  # Reset the index
#             self.user_input_stack = []  # Reset the user input stack for the new round

#         elif self.phase == 1:  # Phase 1: Performing moves
#             print("Performing moves")  # Log the phase
#             if self.idx < len(self.sensor_stack):  # If there are more moves to perform
#                 self.send_move_request(self.sensor_stack[self.idx])  # Send the move request
#                 self.idx += 1  # Increment the index
#             else:
#                 self.phase = 2  # Move to phase 2
#                 self.idx = 0  # Reset the index

#         elif self.phase == 2:  # Phase 2: Sensing user input
#             print("Waiting for user input")  # Log the phase
#             response = self.get_user_input()  # Get user input
#             if response != -1:  # If valid input
#                 self.display_user_selection(response)  # Display the user selection
#                 self.user_input_stack.append(response)  # Add the user input to the user input stack
#                 if self.user_input_stack == self.sensor_stack[:len(self.user_input_stack)]:  # Check if user input matches the sensor stack up to this point
#                     if len(self.user_input_stack) == len(self.sensor_stack):  # If the entire sequence is matched
#                         print("Correct! Moving to the next level.")  # Log the success
#                         self.phase = 0  # Move to phase 0
#                     else:
#                         print("Nice! Keep going")  # Log partial success
#                 else:
#                     print("You failed! Try again.")  # Log the failure
#                     self.sensor_stack = []  # Reset the sensor stack
#                     self.user_input_stack = []  # Reset the user input stack
#                     # self.phase = 0  # Move to phase 0 for retry

#     def display_phase_message(self):  # Method to display phase messages on the screen
#         if self.phase in [0, 1]:
#             message = "Robot's Turn"
#         elif self.phase == 2:
#             message = "Your Turn"
#         elif self.phase == 3:
#             message = "Next Level"
#         else:
#             message = ""
#         img = PILImage.new('RGB', (320, 240), color=(0, 0, 0))  # Create a blank image
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         font = ImageFont.load_default()  # Load the default font
#         d.text((10, 10), message, font=font, fill=(255, 255, 255))  # Draw the message on the image
#         img.save(RELATIVE + 'phase_message.jpg')  # Save the image
#         self.disp.show_image(RELATIVE + 'phase_message.jpg')  # Display the image

#     def display_user_selection(self, selection):  # Method to display user selection
#         img_path = RELATIVE + f'selection_{selection}.jpg'  # Define the image path
#         img = PILImage.new('RGB', (320, 240), color=(0, 0, 0))  # Create a blank image
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         font = ImageFont.load_default()  # Load the default font
#         move_text = MOVES[selection]  # Get the text for the selected move
#         d.text((10, 10), f'You selected: {move_text}', font=font, fill=(255, 255, 255))  # Draw the selection text on the image
#         img.save(img_path)  # Save the image
#         self.disp.show_image(img_path)  # Display the image
#         time.sleep(0.5)  # Display the image for half a second

#     def display(self, pic):  # Method to display an image
#         impath = RELATIVE + pic  # Define the image path
#         print("Displaying: ", impath)  # Log the image path
#         try:
#             img = cv2.imread(impath)  # Read the image using OpenCV
#             if img is None:
#                 raise FileNotFoundError(f"Image not found: {impath}")
#             img = cv2.resize(img, (320, 240))  # Resize the image
#             cv2.imwrite(impath, img)  # Save the resized image
#             self.disp.show_image(impath)  # Display the image
#         except Exception as e:
#             print(f"Error displaying image: {e}")  # Log any errors

# def main():
#     GPIO.setmode(GPIO.BCM)  # Set GPIO mode to BCM
#     GPIO.setup(6, GPIO.IN)  # Set up front sensor pin
#     GPIO.setup(3, GPIO.IN)  # Set up left sensor pin
#     GPIO.setup(16, GPIO.IN)  # Set up right sensor pin

#     rclpy.init()  # Initialize the ROS 2 client library
#     sample_controller = SampleControllerAsync()  # Create an instance of the SampleControllerAsync class

#     try:
#         rclpy.spin(sample_controller)  # Spin the node to keep it active
#     except KeyboardInterrupt:
#         pass
#     finally:
#         sample_controller.destroy_node()  # Destroy the node
#         rclpy.shutdown()  # Shutdown the ROS 2 client library
#         GPIO.cleanup()  # Clean up GPIO settings

# if __name__ == '__main__':
#     main()  # Run the main function if this script is executed


# VERSION 3

# from pupper_interfaces.srv import GoPupper  # Import the GoPupper service definition
# from MangDang.mini_pupper.display import Display, BehaviorState  # Import display and behavior state from mini_pupper
# import rclpy  # Import the ROS 2 Python client library
# from rclpy.node import Node  # Import Node class from ROS 2
# import time  # Import time module for delays
# import RPi.GPIO as GPIO  # Import GPIO library for Raspberry Pi GPIO pin control
# import random  # Import random module for random number generation
# import cv2  # Import OpenCV for image processing
# from cv_bridge import CvBridge  # Import CvBridge to convert ROS image messages to OpenCV images
# from PIL import Image as PILImage, ImageDraw, ImageFont  # Import PIL for image handling
# from sensor_msgs.msg import Image  # Import ROS Image message type

# RELATIVE = "/home/ubuntu/ros2_ws/src/bot/bot/img/"  # Define the relative path for images
# MOVES = ["move_forward", "move_right", "move_left"]  # List of possible movement commands
# COLORS = ["red", "green", "blue"]  # List of colors for display purposes
# LEADERBOARD_FILE = RELATIVE + "leaderboard.txt"  # File to store leaderboard scores
# FONT_PATH = RELATIVE+"arial.ttf"  # Path to the arial.ttf font file

# class SampleControllerAsync(Node):  # Define the main class for the ROS node

#     def __init__(self):
#         super().__init__('sample_controller')  # Initialize the Node with the name 'sample_controller'
#         self.cli = self.create_client(GoPupper, 'pup_command')  # Create a client for the GoPupper service
        
#         self.subscription = None  # Initialize the subscription attribute
#         self.current_frame = None  # Initialize the current frame attribute
#         self.br = CvBridge()  # Initialize CvBridge for converting ROS images to OpenCV
#         self.disp = Display()  # Initialize the display

#         while not self.cli.wait_for_service(timeout_sec=1.0):  # Wait until the GoPupper service is available
#             self.get_logger().info('service not available, waiting again...')  # Log service unavailability
        
#         self.req = GoPupper.Request()  # Initialize the service request object
#         self.sensor_stack = []  # Initialize the list to store sensor stack
#         self.user_input_stack = []  # Initialize the list to store user inputs
#         self.idx = 0  # Initialize the index for tracking sensor stack
#         self.phase = 0  # Initialize the phase variable for game state management
#         self.score = 0  # Initialize the score variable
#         self.scores = []  # Initialize the list to store all scores
#         self.load_scores()  # Load scores from file
#         self.timer = self.create_timer(1.0, self.pupper)  # Create a timer to call the pupper method every second

#     def send_move_request(self, idx):  # Method to send movement requests
#         self.req = GoPupper.Request()  # Create a new request object
#         self.req.command = MOVES[idx]  # Set the command in the request object
#         self.future = self.cli.call_async(self.req)  # Call the service asynchronously
#         return self.future.result()  # Return the result of the service call

#     def get_user_input(self):  # Method to get user input from GPIO
#         tFront = GPIO.input(6)  # Read front sensor
#         tLeft = GPIO.input(3)  # Read left sensor
#         tRight = GPIO.input(16)  # Read right sensor
#         if not tFront:
#             return 0  # Return 0 if front sensor is pressed
#         elif not tRight:
#             return 1  # Return 1 if right sensor is pressed
#         elif not tLeft:
#             return 2  # Return 2 if left sensor is pressed
#         return -1  # Return -1 if no sensor is pressed

#     def cam(self, data):  # Callback method to handle image data
#         try:
#             self.current_frame = self.br.imgmsg_to_cv2(data)  # Convert ROS image message to OpenCV image
#         except Exception as e:
#             self.get_logger().error(f"Error converting image: {e}")

#     def pupper(self):  # Main game logic method
#         self.display_phase_message()  # Display phase message on the screen
#         print("Phase ", self.phase)  # Print the current phase
#         if self.phase == 0:  # Phase 0: Choosing moves
#             new_move = random.randint(0, 2)  # Choose a random move
#             self.sensor_stack.append(new_move)  # Add the new move to the sensor stack
#             print(f"Added move {new_move}")  # Log the added move
#             self.phase = 1  # Move to phase 1
#             self.idx = 0  # Reset the index
#             self.user_input_stack = []  # Reset the user input stack for the new round

#         elif self.phase == 1:  # Phase 1: Performing moves
#             print("Performing moves")  # Log the phase
#             if self.idx < len(self.sensor_stack):  # If there are more moves to perform
#                 self.send_move_request(self.sensor_stack[self.idx])  # Send the move request
#                 self.idx += 1  # Increment the index
#             else:
#                 self.phase = 2  # Move to phase 2
#                 self.idx = 0  # Reset the index

#         elif self.phase == 2:  # Phase 2: Sensing user input
#             print("Waiting for user input")  # Log the phase
#             response = self.get_user_input()  # Get user input
#             if response != -1:  # If valid input
#                 self.display_user_selection(response)  # Display the user selection
#                 self.user_input_stack.append(response)  # Add the user input to the user input stack
#                 if self.user_input_stack == self.sensor_stack[:len(self.user_input_stack)]:  # Check if user input matches the sensor stack up to this point
#                     if len(self.user_input_stack) == len(self.sensor_stack):  # If the entire sequence is matched
#                         self.score += 1  # Increment the score
#                         self.display_custom_message("Correct! \nMoving to the \nnext level.", "green")
#                         print("Correct! Moving to the next level.")  # Log the success
#                         self.phase = 0  # Move to phase 0
#                     else:
#                         self.display_custom_message("Nice! \nKeep going", "black")
#                         print("Nice! Keep going")  # Log partial success
#                 else:
#                     self.display_custom_message("You failed! \nTry again.", "red")
#                     print("You failed! Try again.")  # Log the failure
#                     self.scores.append(self.score)  # Save the score
#                     self.save_scores()  # Save scores to file
#                     self.display_score()  # Display the score
#                     self.display_leaderboard()  # Display the leaderboard
#                     self.phase = 3  # Move to phase 3 (end game)

#         elif self.phase == 3:  # Phase 3: Displaying leaderboard and waiting to play again
#             print("Phase 3: Displaying leaderboard and waiting to play again")  # Log the phase
#             self.display_leaderboard()  # Display the leaderboard
#             time.sleep(5)  # Display the leaderboard for 5 seconds
#             self.display_custom_message("Touch sensor to play again", "black")
#             response = self.get_user_input()  # Get user input to play again
#             if response != -1:  # If a sensor is touched
#                 self.score = 0  # Reset the score
#                 self.sensor_stack = []  # Reset the sensor stack
#                 self.phase = 0  # Move to phase 0 for a new game

#     def display_phase_message(self):  # Method to display phase messages on the screen
#         if self.phase in [0, 1]:
#             message = "Robot's Turn"
#             color = "black"
#         elif self.phase == 2:
#             message = "Your Turn"
#             color = "black"
#         elif self.phase == 3:
#             message = "Next Level"
#             color = "black"
#         else:
#             message = ""
#             color = "black"
#         self.display_custom_message(message, color)

#     def display_user_selection(self, selection):  # Method to display user selection
#         img_path = RELATIVE + f'selection_{selection}.jpg'  # Define the image path
#         img = PILImage.new('RGB', (320, 240), color="black")  # Create a blank image
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         font = ImageFont.truetype(FONT_PATH, 30)  # Load the arial.ttf font with a smaller size
#         move_text = MOVES[selection]  # Get the text for the selected move
#         d.text((10, 10), f'You selected: \n{move_text}', font=font, fill=(255, 255, 255))  # Draw the selection text on the image
#         img.save(img_path)  # Save the image
#         self.disp.show_image(img_path)  # Display the image
#         time.sleep(2)  # Display the image for half a second

#     def display_custom_message(self, message, background_color):  # Method to display custom messages with background color
#         img = PILImage.new('RGB', (320, 240), color=background_color)  # Create a blank image with the given background color
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         # font_size = self.get_optimal_font_size(message)  # Get optimal font size
#         font = ImageFont.truetype(FONT_PATH, 50)  # Load the arial.ttf font with optimal size
#         lines = self.wrap_text(message, font, 300)  # Wrap text to fit within the screen width
#         y_text = 10
#         for line in lines:
#             width, height = d.textsize(line, font=font)
#             d.text(((320 - width) / 2, y_text), line, font=font, fill=(255, 255, 255))
#             y_text += height
#         img_path = RELATIVE + 'custom_message.jpg'
#         img.save(img_path)  # Save the image
#         self.disp.show_image(img_path)  # Display the image
#         time.sleep(2)  # Display the image for half a second

#     # def get_optimal_font_size(self, text, max_width=320, max_height=240):
#     #     font_size = 50  # Start with a large font size
#     #     font = ImageFont.truetype(FONT_PATH, font_size)
#     #     width, height = font.getsize(text)
#     #     while width > max_width or height > max_height:
#     #         font_size -= 1
#     #         font = ImageFont.truetype(FONT_PATH, font_size)
#     #         width, height = font.getsize(text)
#     #     return font_size

#     def wrap_text(self, text, font, max_width):
#         lines = []
#         words = text.split()
#         while words:
#             line = ''
#             while words and font.getsize(line + words[0])[0] <= max_width:
#                 line = line + (words.pop(0) + ' ')
#             lines.append(line.strip())
#         return lines

#     def display_score(self):  # Method to display the user's score
#         self.display_custom_message(f'Your Score: {self.score}', "black")

#     def load_scores(self):  # Method to load scores from a file
#         try:
#             with open(LEADERBOARD_FILE, 'r') as file:
#                 self.scores = [int(line.strip()) for line in file]
#         except FileNotFoundError:
#             self.scores = []

#     def save_scores(self):  # Method to save scores to a file
#         with open(LEADERBOARD_FILE, 'w') as file:
#             for score in self.scores:
#                 file.write(f'{score}\n')

#     def display_leaderboard(self):  # Method to display the leaderboard
#         sorted_scores = sorted(self.scores, reverse=True)[:3]  # Get the top 5 scores
#         leaderboard_message = 'Leaderboard:\n' + '\n'.join([f'{i + 1}. {score}' for i, score in enumerate(sorted_scores)])
#         self.display_custom_message(leaderboard_message, "black")

#     def display(self, pic):  # Method to display an image
#         impath = RELATIVE + pic  # Define the image path
#         print("Displaying: ", impath)  # Log the image path
#         try:
#             img = cv2.imread(impath)  # Read the image using OpenCV
#             if img is None:
#                 raise FileNotFoundError(f"Image not found: {impath}")
#             img = cv2.resize(img, (320, 240))  # Resize the image
#             cv2.imwrite(impath, img)  # Save the resized image
#             self.disp.show_image(impath)  # Display the image
#         except Exception as e:
#             print(f"Error displaying image: {e}")  # Log any errors

# def main():
#     GPIO.setmode(GPIO.BCM)  # Set GPIO mode to BCM
#     GPIO.setup(6, GPIO.IN)  # Set up front sensor pin
#     GPIO.setup(3, GPIO.IN)  # Set up left sensor pin
#     GPIO.setup(16, GPIO.IN)  # Set up right sensor pin

#     rclpy.init()  # Initialize the ROS 2 client library
#     sample_controller = SampleControllerAsync()  # Create an instance of the SampleControllerAsync class

#     try:
#         rclpy.spin(sample_controller)  # Spin the node to keep it active
#     except KeyboardInterrupt:
#         pass
#     finally:
#         sample_controller.destroy_node()  # Destroy the node
#         rclpy.shutdown()  # Shutdown the ROS 2 client library
#         GPIO.cleanup()  # Clean up GPIO settings

# if __name__ == '__main__':
#     main()  # Run the main function if this script is executed

# VERSION 4

# from pupper_interfaces.srv import GoPupper  # Import the GoPupper service definition
# from MangDang.mini_pupper.display import Display, BehaviorState  # Import display and behavior state from mini_pupper
# import rclpy  # Import the ROS 2 Python client library
# from rclpy.node import Node  # Import Node class from ROS 2
# import time  # Import time module for delays
# import RPi.GPIO as GPIO  # Import GPIO library for Raspberry Pi GPIO pin control
# import random  # Import random module for random number generation
# import cv2  # Import OpenCV for image processing
# from cv_bridge import CvBridge  # Import CvBridge to convert ROS image messages to OpenCV images
# from PIL import Image as PILImage, ImageDraw, ImageFont  # Import PIL for image handling
# from sensor_msgs.msg import Image  # Import ROS Image message type

# RELATIVE = "/home/ubuntu/ros2_ws/src/bot/bot/img/"  # Define the relative path for images
# MOVES = ["move_forward", "move_right", "move_left"]  # List of possible movement commands
# COLORS = ["red", "green", "blue"]  # List of colors for display purposes
# LEADERBOARD_FILE = RELATIVE + "leaderboard.txt"  # File to store leaderboard scores
# FONT_PATH = RELATIVE + "arial.ttf"  # Path to the arial.ttf font file

# class SampleControllerAsync(Node):  # Define the main class for the ROS node

#     def __init__(self):
#         super().__init__('sample_controller')  # Initialize the Node with the name 'sample_controller'
#         self.cli = self.create_client(GoPupper, 'pup_command')  # Create a client for the GoPupper service
        
#         self.subscription = None  # Initialize the subscription attribute
#         self.current_frame = None  # Initialize the current frame attribute
#         self.br = CvBridge()  # Initialize CvBridge for converting ROS images to OpenCV
#         self.disp = Display()  # Initialize the display

#         while not self.cli.wait_for_service(timeout_sec=1.0):  # Wait until the GoPupper service is available
#             self.get_logger().info('service not available, waiting again...')  # Log service unavailability
        
#         self.req = GoPupper.Request()  # Initialize the service request object
#         self.sensor_stack = []  # Initialize the list to store sensor stack
#         self.user_input_stack = []  # Initialize the list to store user inputs
#         self.idx = 0  # Initialize the index for tracking sensor stack
#         self.phase = 0  # Initialize the phase variable for game state management
#         self.score = 0  # Initialize the score variable
#         self.scores = []  # Initialize the list to store all scores
#         self.load_scores()  # Load scores from file
#         self.timer = self.create_timer(1.0, self.pupper)  # Create a timer to call the pupper method every second

#     def send_move_request(self, idx):  # Method to send movement requests
#         self.req = GoPupper.Request()  # Create a new request object
#         self.req.command = MOVES[idx]  # Set the command in the request object
#         self.future = self.cli.call_async(self.req)  # Call the service asynchronously
#         return self.future.result()  # Return the result of the service call

#     def get_user_input(self):  # Method to get user input from GPIO
#         tFront = GPIO.input(6)  # Read front sensor
#         tLeft = GPIO.input(3)  # Read left sensor
#         tRight = GPIO.input(16)  # Read right sensor
#         if not tFront:
#             return 0  # Return 0 if front sensor is pressed
#         elif not tRight:
#             return 1  # Return 1 if right sensor is pressed
#         elif not tLeft:
#             return 2  # Return 2 if left sensor is pressed
#         return -1  # Return -1 if no sensor is pressed

#     def cam(self, data):  # Callback method to handle image data
#         try:
#             self.current_frame = self.br.imgmsg_to_cv2(data)  # Convert ROS image message to OpenCV image
#             sorted_scores = sorted(self.scores, reverse=True)
#             position = sorted_scores.index(self.score) + 1
#             img_path = RELATIVE + f'top_{position}.jpg'
#             cv2.imwrite(img_path, self.current_frame)
#         except Exception as e:
#             self.get_logger().error(f"Error converting image: {e}")

#     def pupper(self):  # Main game logic method
#         self.display_phase_message()  # Display phase message on the screen
#         print("Phase ", self.phase)  # Print the current phase
#         if self.phase == 0:  # Phase 0: Choosing moves
#             new_move = random.randint(0, 2)  # Choose a random move
#             self.sensor_stack.append(new_move)  # Add the new move to the sensor stack
#             print(f"Added move {new_move}")  # Log the added move
#             self.phase = 1  # Move to phase 1
#             self.idx = 0  # Reset the index
#             self.user_input_stack = []  # Reset the user input stack for the new round

#         elif self.phase == 1:  # Phase 1: Performing moves
#             print("Performing moves")  # Log the phase
#             if self.idx < len(self.sensor_stack):  # If there are more moves to perform
#                 self.send_move_request(self.sensor_stack[self.idx])  # Send the move request
#                 self.idx += 1  # Increment the index
#             else:
#                 self.phase = 2  # Move to phase 2
#                 self.idx = 0  # Reset the index

#         elif self.phase == 2:  # Phase 2: Sensing user input
#             print("Waiting for user input")  # Log the phase
#             response = self.get_user_input()  # Get user input
#             if response != -1:  # If valid input
#                 self.display_user_selection(response)  # Display the user selection
#                 self.user_input_stack.append(response)  # Add the user input to the user input stack
#                 if self.user_input_stack == self.sensor_stack[:len(self.user_input_stack)]:  # Check if user input matches the sensor stack up to this point
#                     if len(self.user_input_stack) == len(self.sensor_stack):  # If the entire sequence is matched
#                         self.score += 1  # Increment the score
#                         self.display_custom_message("Correct! Moving to the next level.", "green")
#                         print("Correct! Moving to the next level.")  # Log the success
#                         self.phase = 0  # Move to phase 0
#                     else:
#                         self.display_custom_message("Nice! Keep going", "black")
#                         print("Nice! Keep going")  # Log partial success
#                 else:
#                     self.display_custom_message("You failed! Try again.", "red")
#                     print("You failed! Try again.")  # Log the failure
#                     self.scores.append(self.score)  # Save the score
#                     self.save_scores()  # Save scores to file
#                     # self.display_score()  # Display the score
#                     # self.display_leaderboard()  # Display the leaderboard
#                     self.sensor_stack = []
#                     self.phase = 3  # Move to phase 3 (end game)

#         # Phase 3: Start cam
#         if self.phase == 3:
#             self.subscription = self.create_subscription(Image, '/oak/rgb/image_raw', self.cam, 10)
#             self.phase = 4

#         # Phase 4: Pick Color
#         if self.phase == 4:
#             print("Pick Color")
#             new_color = random.randint(0, 2)
#             self.sensor_stack.append(new_color)
#             print("Added color ", new_color)
#             self.phase = 5
#             self.idx = 0
        
#         # Phase 5: Show Color
#         if self.phase == 5:
#             print("Show Color")
#             if self.idx < len(self.sensor_stack):
#                 self.display(COLORS[self.sensor_stack[self.idx]]+".jpg")
#                 self.idx += 1
#             else:
#                 self.phase = 6
#                 self.idx = 0

#         # Phase 6: Viewing Colors
#         if self.phase == 6:
#             print("Response")
#             hsv = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2HSV)

#             blue_mask = cv2.inRange(hsv, (55, 50, 50), (130, 255, 255))
#             red_mask = cv2.inRange(hsv, (160, 50, 50), (180, 255, 255))
#             green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))

#             blue_masked_frame = cv2.bitwise_and(self.current_frame, self.current_frame, mask=blue_mask)
#             red_masked_frame = cv2.bitwise_and(self.current_frame, self.current_frame, mask=red_mask)
#             green_masked_frame = cv2.bitwise_and(self.current_frame, self.current_frame, mask=green_mask)       
#             cols = [blue_masked_frame, red_masked_frame, green_masked_frame]

#             if cv2.countNonZero(cols[self.sensor_stack[self.idx]]) > 15:
#                 self.idx += 1
#                 self.score += 1
#                 print("Nice! Keep going")
#                 if self.idx >= len(self.sensor_stack):
#                     print("Correct! Moving to the next level.")
#                     self.phase = 3
#             elif cv2.countNonZero(blue_masked_frame) > 15 or cv2.countNonZero(red_masked_frame) > 15 or cv2.countNonZero(green_masked_frame) > 15:
#                 print("You failed! Try again.")
#                 self.sensor_stack = []
#                 self.phase = 7

#         # Phase 7: Picture
#         if self.phase == 7:
#             print("Picture")
#             cv2.imwrite(RELATIVE+"pic.jpg", self.current_frame)
#             self.display("pic.jpg")
#             self.phase = 8

#         elif self.phase == 8:  # Phase 5: Display leaderboard and waiting to play again
#             print("Phase 5: Displaying leaderboard and waiting to play again")  # Log the phase
#             self.display_leaderboard()  # Display the leaderboard
#             time.sleep(5)  # Display the leaderboard for 5 seconds
#             self.display_custom_message("Touch sensor to play again", "black")
#             response = self.get_user_input()  # Get user input to play again
#             if response != -1:  # If a sensor is touched
#                 self.score = 0  # Reset the score
#                 self.sensor_stack = []  # Reset the sensor stack
#                 self.phase = 0  # Move to phase 0 for a new game

#     def display_phase_message(self):  # Method to display phase messages on the screen
#         if self.phase in [0, 1]:
#             message = "Robot's Turn"
#             color = "black"
#         elif self.phase == 2:
#             message = "Your Turn"
#             color = "black"
#         elif self.phase == 3:
#             message = "Next Level"
#             color = "black"
#         else:
#             message = ""
#             color = "black"
#         self.display_custom_message(message, color)

#     def display_user_selection(self, selection):  # Method to display user selection
#         img_path = RELATIVE + f'selection_{selection}.jpg'  # Define the image path
#         img = PILImage.new('RGB', (320, 240), color="black")  # Create a blank image
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         font = ImageFont.truetype(FONT_PATH, 30)  # Load the arial.ttf font with a smaller size
#         move_text = MOVES[selection]  # Get the text for the selected move
#         d.text((10, 10), f'You selected: {move_text}', font=font, fill=(255, 255, 255))  # Draw the selection text on the image
#         img.save(img_path)  # Save the image
#         self.disp.show_image(img_path)  # Display the image
#         time.sleep(0.5)  # Display the image for half a second

#     def display_custom_message(self, message, background_color):  # Method to display custom messages with background color
#         img = PILImage.new('RGB', (320, 240), color=background_color)  # Create a blank image with the given background color
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         font_size = self.get_optimal_font_size(message)  # Get optimal font size
#         font = ImageFont.truetype(FONT_PATH, font_size)  # Load the arial.ttf font with optimal size
#         lines = self.wrap_text(message, font, 300)  # Wrap text to fit within the screen width
#         y_text = 10
#         for line in lines:
#             width, height = d.textsize(line, font=font)
#             d.text(((320 - width) / 2, y_text), line, font=font, fill=(255, 255, 255))
#             y_text += height
#         img_path = RELATIVE + 'custom_message.jpg'
#         img.save(img_path)  # Save the image
#         self.disp.show_image(img_path)  # Display the image
#         time.sleep(0.5)  # Display the image for half a second

#     def get_optimal_font_size(self, text, max_width=320, max_height=240):
#         font_size = 50  # Start with a large font size
#         font = ImageFont.truetype(FONT_PATH, font_size)
#         width, height = font.getsize(text)
#         while width > max_width or height > max_height:
#             font_size -= 1
#             font = ImageFont.truetype(FONT_PATH, font_size)
#             width, height = font.getsize(text)
#         return font_size

#     def wrap_text(self, text, font, max_width):
#         lines = []
#         words = text.split()
#         while words:
#             line = ''
#             while words and font.getsize(line + words[0])[0] <= max_width:
#                 line = line + (words.pop(0) + ' ')
#             lines.append(line.strip())
#         return lines

#     def display_score(self):  # Method to display the user's score
#         self.display_custom_message(f'Your Score: {self.score}', "black")

#     def load_scores(self):  # Method to load scores from a file
#         try:
#             with open(LEADERBOARD_FILE, 'r') as file:
#                 self.scores = [int(line.strip()) for line in file]
#         except FileNotFoundError:
#             self.scores = []

#     def save_scores(self):  # Method to save scores to a file
#         with open(LEADERBOARD_FILE, 'w') as file:
#             for score in self.scores:
#                 file.write(f'{score}\n')

#     def display_leaderboard(self):  # Method to display the leaderboard
#         sorted_scores = sorted(self.scores, reverse=True)[:3]  # Get the top 3 scores
#         leaderboard_message = 'Leaderboard:\n' + '\n'.join([f'{i + 1}. {score}' for i, score in enumerate(sorted_scores)])
#         self.display_multiline_message(leaderboard_message, "black")
#         for i, score in enumerate(sorted_scores):
#             pic_path = RELATIVE + f'top_{i + 1}.jpg'
#             self.display(pic_path)
#             time.sleep(1)

#     def display_multiline_message(self, message, background_color):  # Method to display custom messages with background color
#         img = PILImage.new('RGB', (320, 240), color=background_color)  # Create a blank image with the given background color
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         font_size = 30  # Start with a reasonable font size
#         font = ImageFont.truetype(FONT_PATH, font_size)  # Load the arial.ttf font with the starting size
#         lines = message.split('\n')  # Split the message into lines
#         y_text = 10
#         for line in lines:
#             while font.getsize(line)[0] > 320:  # Reduce font size if the line is too wide
#                 font_size -= 1
#                 font = ImageFont.truetype(FONT_PATH, font_size)
#             d.text((10, y_text), line, font=font, fill=(255, 255, 255))
#             y_text += font.getsize(line)[1] + 5  # Increment y position for the next line with some padding
#         img_path = RELATIVE + 'custom_message.jpg'
#         img.save(img_path)  # Save the image
#         self.disp.show_image(img_path)  # Display the image
#         time.sleep(0.5)  # Display the image for half a second

#     def display(self, pic):  # Method to display an image
#         impath = RELATIVE + pic  # Define the image path
#         print("Displaying: ", impath)  # Log the image path
#         try:
#             img = cv2.imread(impath)  # Read the image using OpenCV
#             if img is None:
#                 raise FileNotFoundError(f"Image not found: {impath}")
#             img = cv2.resize(img, (320, 240))  # Resize the image
#             cv2.imwrite(impath, img)  # Save the resized image
#             self.disp.show_image(impath)  # Display the image
#         except Exception as e:
#             print(f"Error displaying image: {e}")  # Log any errors

# def main():
#     GPIO.setmode(GPIO.BCM)  # Set GPIO mode to BCM
#     GPIO.setup(6, GPIO.IN)  # Set up front sensor pin
#     GPIO.setup(3, GPIO.IN)  # Set up left sensor pin
#     GPIO.setup(16, GPIO.IN)  # Set up right sensor pin

#     rclpy.init()  # Initialize the ROS 2 client library
#     sample_controller = SampleControllerAsync()  # Create an instance of the SampleControllerAsync class

#     try:
#         rclpy.spin(sample_controller)  # Spin the node to keep it active
#     except KeyboardInterrupt:
#         pass
#     finally:
#         sample_controller.destroy_node()  # Destroy the node
#         rclpy.shutdown()  # Shutdown the ROS 2 client library
#         GPIO.cleanup()  # Clean up GPIO settings

# if __name__ == '__main__':
#     main()  # Run the main function if this script is executed\


# VERSION 5

# from pupper_interfaces.srv import GoPupper  # Import the GoPupper service definition
# from MangDang.mini_pupper.display import Display, BehaviorState  # Import display and behavior state from mini_pupper
# import rclpy  # Import the ROS 2 Python client library
# from rclpy.node import Node  # Import Node class from ROS 2
# import time  # Import time module for delays
# import RPi.GPIO as GPIO  # Import GPIO library for Raspberry Pi GPIO pin control
# import random  # Import random module for random number generation
# import cv2  # Import OpenCV for image processing
# from cv_bridge import CvBridge  # Import CvBridge to convert ROS image messages to OpenCV images
# from PIL import Image as PILImage, ImageDraw, ImageFont  # Import PIL for image handling
# from sensor_msgs.msg import Image  # Import ROS Image message type

# RELATIVE = "/home/ubuntu/ros2_ws/src/bot/bot/img/"  # Define the relative path for images
# MOVES = ["move_forward", "move_right", "move_left"]  # List of possible movement commands
# COLORS = ["red", "green", "blue"]  # List of colors for display purposes
# LEADERBOARD_FILE = RELATIVE + "leaderboard.txt"  # File to store leaderboard scores
# FONT_PATH = RELATIVE + "arial.ttf"  # Path to the arial.ttf font file

# class SampleControllerAsync(Node):  # Define the main class for the ROS node

#     def __init__(self):
#         super().__init__('sample_controller')  # Initialize the Node with the name 'sample_controller'
#         self.cli = self.create_client(GoPupper, 'pup_command')  # Create a client for the GoPupper service
        
#         self.subscription = None  # Initialize the subscription attribute
#         self.current_frame = None  # Initialize the current frame attribute
#         self.br = CvBridge()  # Initialize CvBridge for converting ROS images to OpenCV
#         self.disp = Display()  # Initialize the display

#         while not self.cli.wait_for_service(timeout_sec=1.0):  # Wait until the GoPupper service is available
#             self.get_logger().info('service not available, waiting again...')  # Log service unavailability
        
#         self.req = GoPupper.Request()  # Initialize the service request object
#         self.sensor_stack = []  # Initialize the list to store sensor stack
#         self.user_input_stack = []  # Initialize the list to store user inputs
#         self.idx = 0  # Initialize the index for tracking sensor stack
#         self.phase = 0  # Initialize the phase variable for game state management
#         self.score = 0  # Initialize the score variable
#         self.scores = []  # Initialize the list to store all scores
#         self.load_scores()  # Load scores from file
#         self.timer = self.create_timer(1.0, self.pupper)  # Create a timer to call the pupper method every second

#     def send_move_request(self, idx):  # Method to send movement requests
#         self.req = GoPupper.Request()  # Create a new request object
#         self.req.command = MOVES[idx]  # Set the command in the request object
#         self.future = self.cli.call_async(self.req)  # Call the service asynchronously
#         return self.future.result()  # Return the result of the service call

#     def get_user_input(self):  # Method to get user input from GPIO
#         tFront = GPIO.input(6)  # Read front sensor
#         tLeft = GPIO.input(3)  # Read left sensor
#         tRight = GPIO.input(16)  # Read right sensor
#         if not tFront:
#             return 0  # Return 0 if front sensor is pressed
#         elif not tRight:
#             return 1  # Return 1 if right sensor is pressed
#         elif not tLeft:
#             return 2  # Return 2 if left sensor is pressed
#         return -1  # Return -1 if no sensor is pressed

#     def cam(self, data):  # Callback method to handle image data
#         try:
#             self.current_frame = self.br.imgmsg_to_cv2(data)  # Convert ROS image message to OpenCV image
#             sorted_scores = sorted(self.scores, reverse=True)
#             position = sorted_scores.index(self.score) + 1
#             img_path = f'top_{position}.jpg'
#             cv2.imwrite(img_path, self.current_frame)
#             self.subscription = None  # Unsubscribe after capturing the image
#         except Exception as e:
#             self.get_logger().error(f"Error converting image: {e}")

#     def pupper(self):  # Main game logic method
#         self.display_phase_message()  # Display phase message on the screen
#         print("Phase ", self.phase)  # Print the current phase
#         if self.phase == 0:  # Phase 0: Choosing moves
#             new_move = random.randint(0, 2)  # Choose a random move
#             self.sensor_stack.append(new_move)  # Add the new move to the sensor stack
#             print(f"Added move {new_move}")  # Log the added move
#             self.phase = 1  # Move to phase 1
#             self.idx = 0  # Reset the index
#             self.user_input_stack = []  # Reset the user input stack for the new round

#         elif self.phase == 1:  # Phase 1: Performing moves
#             print("Performing moves")  # Log the phase
#             if self.idx < len(self.sensor_stack):  # If there are more moves to perform
#                 self.send_move_request(self.sensor_stack[self.idx])  # Send the move request
#                 self.idx += 1  # Increment the index
#             else:
#                 self.phase = 2  # Move to phase 2
#                 self.idx = 0  # Reset the index

#         elif self.phase == 2:  # Phase 2: Sensing user input
#             print("Waiting for user input")  # Log the phase
#             response = self.get_user_input()  # Get user input
#             if response != -1:  # If valid input
#                 self.display_user_selection(response)  # Display the user selection
#                 self.user_input_stack.append(response)  # Add the user input to the user input stack
#                 if self.user_input_stack == self.sensor_stack[:len(self.user_input_stack)]:  # Check if user input matches the sensor stack up to this point
#                     if len(self.user_input_stack) == len(self.sensor_stack):  # If the entire sequence is matched
#                         self.score += 1  # Increment the score
#                         self.display_custom_message("Correct! Moving to the next level.", "green")
#                         print("Correct! Moving to the next level.")  # Log the success
#                         self.phase = 0  # Move to phase 0
#                     else:
#                         self.display_custom_message("Nice! Keep going", "black")
#                         print("Nice! Keep going")  # Log partial success
#                 else:
#                     self.display_custom_message("You failed! Try again.", "red")
#                     print("You failed! Try again.")  # Log the failure
#                     self.scores.append(self.score)  # Save the score
#                     self.save_scores()  # Save scores to file
#                     # self.display_score()  # Display the score
#                     # self.display_leaderboard()  # Display the leaderboard
#                     self.phase = 3  # Move to phase 3 (end game)

#         elif self.phase == 3:  # Phase 3: Ask for a picture
#             print("Phase 3: Ask for a picture")  # Log the phase
#             self.display_custom_message("Take a picture?\nLeft: Yes, Right: No", "black")
#             response = self.get_user_input()  # Get user input
#             if response == 1:  # Left sensor for yes
#                 self.phase = 4  # Move to phase 4 (taking picture)
#             elif response == 2:  # Right sensor for no
#                 self.phase = 5  # Move to phase 5 (display leaderboard without picture)

#         elif self.phase == 4:  # Phase 4: Taking picture with countdown
#             print("Phase 4: Taking picture with countdown")  # Log the phase
#             self.display_custom_message("3", "black")
#             time.sleep(1)
#             self.display_custom_message("2", "black")
#             time.sleep(1)
#             self.display_custom_message("1", "black")
#             time.sleep(1)
#             self.display_custom_message("Say Cheese!", "black")
#             time.sleep(1)
#             self.subscription = self.create_subscription(Image, '/oak/rgb/image_raw', self.cam, 10)
#             time.sleep(2)  # Allow some time for the image to be captured
#             self.display_custom_message("Photo taken!", "black")
#             time.sleep(1)
#             self.phase = 5  # Move to phase 5 (display leaderboard)

#         elif self.phase == 5:  # Phase 5: Display leaderboard and waiting to play again
#             print("Phase 5: Displaying leaderboard and waiting to play again")  # Log the phase
#             self.display_leaderboard()  # Display the leaderboard
#             time.sleep(5)  # Display the leaderboard for 5 seconds
#             self.display_custom_message("Touch sensor to play again", "black")
#             response = self.get_user_input()  # Get user input to play again
#             if response != -1:  # If a sensor is touched
#                 self.score = 0  # Reset the score
#                 self.sensor_stack = []  # Reset the sensor stack
#                 self.phase = 0  # Move to phase 0 for a new game

#     def display_phase_message(self):  # Method to display phase messages on the screen
#         if self.phase in [0, 1]:
#             message = "Robot's Turn"
#             color = "black"
#         elif self.phase == 2:
#             message = "Your Turn"
#             color = "black"
#         elif self.phase == 3:
#             message = "Next Level"
#             color = "black"
#         else:
#             message = ""
#             color = "black"
#         self.display_custom_message(message, color)

#     def display_user_selection(self, selection):  # Method to display user selection
#         img_path = RELATIVE + f'selection_{selection}.jpg'  # Define the image path
#         img = PILImage.new('RGB', (320, 240), color="black")  # Create a blank image
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         font = ImageFont.truetype(FONT_PATH, 30)  # Load the arial.ttf font with a smaller size
#         move_text = MOVES[selection]  # Get the text for the selected move
#         d.text((10, 10), f'You selected: {move_text}', font=font, fill=(255, 255, 255))  # Draw the selection text on the image
#         img.save(img_path)  # Save the image
#         self.disp.show_image(img_path)  # Display the image
#         time.sleep(0.5)  # Display the image for half a second

#     def display_custom_message(self, message, background_color):  # Method to display custom messages with background color
#         img = PILImage.new('RGB', (320, 240), color=background_color)  # Create a blank image with the given background color
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         font_size = self.get_optimal_font_size(message)  # Get optimal font size
#         font = ImageFont.truetype(FONT_PATH, font_size)  # Load the arial.ttf font with optimal size
#         lines = self.wrap_text(message, font, 300)  # Wrap text to fit within the screen width
#         y_text = 10
#         for line in lines:
#             width, height = d.textsize(line, font=font)
#             d.text(((320 - width) / 2, y_text), line, font=font, fill=(255, 255, 255))
#             y_text += height
#         img_path = RELATIVE + 'custom_message.jpg'
#         img.save(img_path)  # Save the image
#         self.disp.show_image(img_path)  # Display the image
#         time.sleep(0.5)  # Display the image for half a second

#     def get_optimal_font_size(self, text, max_width=320, max_height=240):
#         font_size = 50  # Start with a large font size
#         font = ImageFont.truetype(FONT_PATH, font_size)
#         width, height = font.getsize(text)
#         while width > max_width or height > max_height:
#             font_size -= 1
#             font = ImageFont.truetype(FONT_PATH, font_size)
#             width, height = font.getsize(text)
#         return font_size

#     def wrap_text(self, text, font, max_width):
#         lines = []
#         words = text.split()
#         while words:
#             line = ''
#             while words and font.getsize(line + words[0])[0] <= max_width:
#                 line = line + (words.pop(0) + ' ')
#             lines.append(line.strip())
#         return lines

#     def display_score(self):  # Method to display the user's score
#         self.display_custom_message(f'Your Score: {self.score}', "black")

#     def load_scores(self):  # Method to load scores from a file
#         try:
#             with open(LEADERBOARD_FILE, 'r') as file:
#                 self.scores = [int(line.strip()) for line in file]
#         except FileNotFoundError:
#             self.scores = []

#     def save_scores(self):  # Method to save scores to a file
#         with open(LEADERBOARD_FILE, 'w') as file:
#             for score in self.scores:
#                 file.write(f'{score}\n')

#     def display_leaderboard(self):  # Method to display the leaderboard
#         sorted_scores = sorted(self.scores, reverse=True)[:3]  # Get the top 3 scores
#         leaderboard_message = 'Leaderboard:\n' + '\n'.join([f'{i + 1}. {score}' for i, score in enumerate(sorted_scores)])
#         self.display_multiline_message(leaderboard_message, "black")
#         for i, score in enumerate(sorted_scores):
#             pic_path = f'top_{i + 1}.jpg'
#             self.display(pic_path)
#             time.sleep(2)

#     def display_multiline_message(self, message, background_color):  # Method to display custom messages with background color
#         img = PILImage.new('RGB', (320, 240), color=background_color)  # Create a blank image with the given background color
#         d = ImageDraw.Draw(img)  # Initialize the drawing context
#         font_size = 30  # Start with a reasonable font size
#         font = ImageFont.truetype(FONT_PATH, font_size)  # Load the arial.ttf font with the starting size
#         lines = message.split('\n')  # Split the message into lines
#         y_text = 10
#         for line in lines:
#             while font.getsize(line)[0] > 320:  # Reduce font size if the line is too wide
#                 font_size -= 1
#                 font = ImageFont.truetype(FONT_PATH, font_size)
#             d.text((10, y_text), line, font=font, fill=(255, 255, 255))
#             y_text += font.getsize(line)[1] + 5  # Increment y position for the next line with some padding
#         img_path = RELATIVE + 'custom_message.jpg'
#         img.save(img_path)  # Save the image
#         self.disp.show_image(img_path)  # Display the image
#         time.sleep(0.5)  # Display the image for half a second

#     def display(self, pic):  # Method to display an image
#         impath = RELATIVE + pic  # Define the image path
#         print("Displaying: ", impath)  # Log the image path
#         try:
#             img = cv2.imread(impath)  # Read the image using OpenCV
#             if img is None:
#                 raise FileNotFoundError(f"Image not found: {impath}")
#             img = cv2.resize(img, (320, 240))  # Resize the image
#             cv2.imwrite(impath, img)  # Save the resized image
#             self.disp.show_image(impath)  # Display the image
#         except Exception as e:
#             print(f"Error displaying image: {e}")  # Log any errors

# def main():
#     GPIO.setmode(GPIO.BCM)  # Set GPIO mode to BCM
#     GPIO.setup(6, GPIO.IN)  # Set up front sensor pin
#     GPIO.setup(3, GPIO.IN)  # Set up left sensor pin
#     GPIO.setup(16, GPIO.IN)  # Set up right sensor pin

#     rclpy.init()  # Initialize the ROS 2 client library
#     sample_controller = SampleControllerAsync()  # Create an instance of the SampleControllerAsync class

#     try:
#         rclpy.spin(sample_controller)  # Spin the node to keep it active
#     except KeyboardInterrupt:
#         pass
#     finally:
#         sample_controller.destroy_node()  # Destroy the node
#         rclpy.shutdown()  # Shutdown the ROS 2 client library
#         GPIO.cleanup()  # Clean up GPIO settings

# if __name__ == '__main__':
#     main()  # Run the main function if this script is executed

# VERSION 6

from pupper_interfaces.srv import GoPupper  # Import the GoPupper service definition
from MangDang.mini_pupper.display import Display, BehaviorState  # Import display and behavior state from mini_pupper
import rclpy  # Import the ROS 2 Python client library
from rclpy.node import Node  # Import Node class from ROS 2
import time  # Import time module for delays
import RPi.GPIO as GPIO  # Import GPIO library for Raspberry Pi GPIO pin control
import random  # Import random module for random number generation
import cv2  # Import OpenCV for image processing
from cv_bridge import CvBridge  # Import CvBridge to convert ROS image messages to OpenCV images
from PIL import Image as PILImage, ImageDraw, ImageFont  # Import PIL for image handling
from sensor_msgs.msg import Image  # Import ROS Image message type
import os  # Import os module for file operations

RELATIVE = "/home/ubuntu/ros2_ws/src/bot/bot/img/"  # Define the relative path for images
MOVES = ["move_forward", "move_right", "move_left"]  # List of possible movement commands
COLORS = ["red", "green", "blue"]  # List of colors for display purposes
LEADERBOARD_FILE = RELATIVE + "leaderboard.txt"  # File to store leaderboard scores
FONT_PATH = RELATIVE + "arial.ttf"  # Path to the arial.ttf font file

class SampleControllerAsync(Node):  # Define the main class for the ROS node

    def __init__(self):
        super().__init__('sample_controller')  # Initialize the Node with the name 'sample_controller'
        self.cli = self.create_client(GoPupper, 'pup_command')  # Create a client for the GoPupper service
        
        self.subscription = self.create_subscription(Image, '/oak/rgb/image_raw', self.cam, 1) # Initialize the subscription attribute
        # self.subscription = None  
        self.current_frame = None  # Initialize the current frame attribute
        self.br = CvBridge()  # Initialize CvBridge for converting ROS images to OpenCV
        self.disp = Display()  # Initialize the display
        

        while not self.cli.wait_for_service(timeout_sec=1.0):  # Wait until the GoPupper service is available
            self.get_logger().info('service not available, waiting again...')  # Log service unavailability
        
        self.req = GoPupper.Request()  # Initialize the service request object
        self.sensor_stack = []  # Initialize the list to store sensor stack
        self.user_input_stack = []  # Initialize the list to store user inputs
        self.idx = 0  # Initialize the index for tracking sensor stack
        self.phase = 0  # Initialize the phase variable for game state management
        self.score = 0  # Initialize the score variable
        self.scores = []  # Initialize the list to store all scores
        self.load_scores()  # Load scores from file
        self.timer = self.create_timer(1.0, self.pupper)  # Create a timer to call the pupper method every second

    def send_move_request(self, idx):  # Method to send movement requests
        self.req = GoPupper.Request()  # Create a new request object
        self.req.command = MOVES[idx]  # Set the command in the request object
        self.future = self.cli.call_async(self.req)  # Call the service asynchronously
        return self.future.result()  # Return the result of the service call

    def get_user_input(self):  # Method to get user input from GPIO
        tFront = GPIO.input(6)  # Read front sensor
        tLeft = GPIO.input(3)  # Read left sensor
        tRight = GPIO.input(16)  # Read right sensor
        if not tFront:
            return 0  # Return 0 if front sensor is pressed
        elif not tRight:
            return 1  # Return 1 if right sensor is pressed
        elif not tLeft:
            return 2  # Return 2 if left sensor is pressed
        return -1  # Return -1 if no sensor is pressed

    def cam(self, data):  # Callback method to handle image data
        try:
            if not self.capture_image:
                return

            # Convert ROS image message to OpenCV image
            self.current_frame = self.br.imgmsg_to_cv2(data)
            
            if self.current_frame is None:
                self.get_logger().error("No image data in current_frame")
                return
            
            # Sort the scores and determine the image position
            sorted_scores = sorted(self.scores, reverse=True)
            if self.score not in sorted_scores:
                self.get_logger().error("Score not found in sorted_scores")
                return
            
            position = sorted_scores.index(self.score) + 1
            img_path = f'top_{position}.jpg'
            
            # Save the image
            success = cv2.imwrite(img_path, self.current_frame)
            if not success:
                self.get_logger().error(f"Failed to write image to {img_path}")
            else:
                self.get_logger().info(f"Image successfully saved to {img_path}")
            
            # Reset the capture flag
            self.capture_image = False
            
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")

    def pupper(self):  # Main game logic method
        self.display_phase_message()  # Display phase message on the screen
        print("Phase ", self.phase)  # Print the current phase
        if self.phase == 0:  # Phase 0: Choosing moves
            new_move = random.randint(0, 2)  # Choose a random move
            self.sensor_stack.append(new_move)  # Add the new move to the sensor stack
            print(f"Added move {new_move}")  # Log the added move
            self.phase = 1  # Move to phase 1
            self.idx = 0  # Reset the index
            self.user_input_stack = []  # Reset the user input stack for the new round

        elif self.phase == 1:  # Phase 1: Performing moves
            print("Performing moves")  # Log the phase
            if self.idx < len(self.sensor_stack):  # If there are more moves to perform
                self.send_move_request(self.sensor_stack[self.idx])  # Send the move request
                self.idx += 1  # Increment the index
            else:
                self.phase = 2  # Move to phase 2
                self.idx = 0  # Reset the index

        elif self.phase == 2:  # Phase 2: Sensing user input
            print("Waiting for user input")  # Log the phase
            response = self.get_user_input()  # Get user input
            if response != -1:  # If valid input
                self.display_user_selection(response)  # Display the user selection
                self.user_input_stack.append(response)  # Add the user input to the user input stack
                if self.user_input_stack == self.sensor_stack[:len(self.user_input_stack)]:  # Check if user input matches the sensor stack up to this point
                    if len(self.user_input_stack) == len(self.sensor_stack):  # If the entire sequence is matched
                        self.score += 1  # Increment the score
                        self.display_custom_message("Correct! Moving to the next level.", "green")
                        print("Correct! Moving to the next level.")  # Log the success
                        self.phase = 0  # Move to phase 0
                    else:
                        self.display_custom_message("Nice! Keep going", "black")
                        print("Nice! Keep going")  # Log partial success
                else:
                    self.display_custom_message("You failed! Try again.", "red")
                    print("You failed! Try again.")  # Log the failure
                    self.scores.append(self.score)  # Save the score
                    self.save_scores()  # Save scores to file
                    self.phase = 3  # Move to phase 3 (end game)

        elif self.phase == 3:  # Phase 3: Ask for a picture
            print("Phase 3: Ask for a picture")  # Log the phase
            self.display_custom_message("Take a picture?\nLeft: Yes, Right: No", "black")
            response = self.get_user_input()  # Get user input
            if response == 1:  # Left sensor for yes
                self.phase = 4  # Move to phase 4 (taking picture)
            elif response == 2:  # Right sensor for no
                self.phase = 5  # Move to phase 5 (display leaderboard without picture)

        elif self.phase == 4:  # Phase 4: Taking picture with countdown
            print("Phase 4: Taking picture with countdown")  # Log the phase
            self.display_custom_message("3", "black")
            time.sleep(1)
            self.display_custom_message("2", "black")
            time.sleep(1)
            self.display_custom_message("1", "black")
            time.sleep(1)
            self.display_custom_message("Say Cheese!", "black")
            self.capture = True
            time.sleep(3) # Allow some time for the image to be captured
            self.display_custom_message("Photo taken!", "black")
            time.sleep(1)
            self.phase = 5  # Move to phase 5 (display leaderboard)

        elif self.phase == 5:  # Phase 5: Display leaderboard and waiting to play again
            print("Phase 5: Displaying leaderboard and waiting to play again")  # Log the phase
            self.display_leaderboard()  # Display the leaderboard
            time.sleep(5)  # Display the leaderboard for 5 seconds
            self.display_custom_message("Touch sensor to play again", "black")
            response = self.get_user_input()  # Get user input to play again
            if response != -1:  # If a sensor is touched
                self.score = 0  # Reset the score
                self.sensor_stack = []  # Reset the sensor stack
                self.phase = 0  # Move to phase 0 for a new game

    def display_phase_message(self):  # Method to display phase messages on the screen
        if self.phase in [0, 1]:
            message = "Robot's Turn"
            color = "black"
        elif self.phase == 2:
            message = "Your Turn"
            color = "black"
        elif self.phase == 3:
            message = "Next Level"
            color = "black"
        else:
            message = ""
            color = "black"
        self.display_custom_message(message, color)

    def display_user_selection(self, selection):  # Method to display user selection
        img_path = RELATIVE + f'selection_{selection}.jpg'  # Define the image path
        img = PILImage.new('RGB', (320, 240), color="black")  # Create a blank image
        d = ImageDraw.Draw(img)  # Initialize the drawing context
        font = ImageFont.truetype(FONT_PATH, 30)  # Load the arial.ttf font with a smaller size
        move_text = MOVES[selection]  # Get the text for the selected move
        d.text((10, 10), f'You selected: \n{move_text}', font=font, fill=(255, 255, 255))  # Draw the selection text on the image
        img.save(img_path)  # Save the image
        self.disp.show_image(img_path)  # Display the image
        time.sleep(0.5)  # Display the image for half a second

    def display_custom_message(self, message, background_color):  # Method to display custom messages with background color
        img = PILImage.new('RGB', (320, 240), color=background_color)  # Create a blank image with the given background color
        d = ImageDraw.Draw(img)  # Initialize the drawing context
        font_size = self.get_optimal_font_size(message)  # Get optimal font size
        font = ImageFont.truetype(FONT_PATH, font_size)  # Load the arial.ttf font with optimal size
        lines = self.wrap_text(message, font, 300)  # Wrap text to fit within the screen width
        y_text = 10
        for line in lines:
            width, height = d.textsize(line, font=font)
            d.text(((320 - width) / 2, y_text), line, font=font, fill=(255, 255, 255))
            y_text += height
        img_path = RELATIVE + 'custom_message.jpg'
        img.save(img_path)  # Save the image
        self.disp.show_image(img_path)  # Display the image
        time.sleep(0.5)  # Display the image for half a second

    def get_optimal_font_size(self, text, max_width=320, max_height=240):
        font_size = 50  # Start with a large font size
        font = ImageFont.truetype(FONT_PATH, font_size)
        width, height = font.getsize(text)
        while width > max_width or height > max_height:
            font_size -= 1
            font = ImageFont.truetype(FONT_PATH, font_size)
            width, height = font.getsize(text)
        return font_size

    def wrap_text(self, text, font, max_width):
        lines = []
        words = text.split()
        while words:
            line = ''
            while words and font.getsize(line + words[0])[0] <= max_width:
                line = line + (words.pop(0) + ' ')
            lines.append(line.strip())
        return lines

    def display_score(self):  # Method to display the user's score
        self.display_custom_message(f'Your Score: {self.score}', "black")

    def load_scores(self):  # Method to load scores from a file
        try:
            with open(LEADERBOARD_FILE, 'r') as file:
                try: 
                    self.scores = [int(line.strip()) for line in file]
                except:
                    self.scores = []
        except FileNotFoundError:
            self.scores = []

    def save_scores(self):  # Method to save scores to a file
        with open(LEADERBOARD_FILE, 'w') as file:
            for score in self.scores:
                file.write(f'{score}\n')

    def display_leaderboard(self):  # Method to display the leaderboard
        sorted_scores = sorted(self.scores, reverse=True)[:3]  # Get the top 3 scores
        leaderboard_message = 'Leaderboard:\n' + '\n'.join([f'{i + 1}. {score}' for i, score in enumerate(sorted_scores)])
        self.display_multiline_message(leaderboard_message, "black")
        for i, score in enumerate(sorted_scores):
            pic_path = f'top_{i + 1}.jpg'
            self.display(pic_path)
            time.sleep(2)

    def display_multiline_message(self, message, background_color):  # Method to display custom messages with background color
        img = PILImage.new('RGB', (320, 240), color=background_color)  # Create a blank image with the given background color
        d = ImageDraw.Draw(img)  # Initialize the drawing context
        font_size = 30  # Start with a reasonable font size
        font = ImageFont.truetype(FONT_PATH, font_size)  # Load the arial.ttf font with the starting size
        lines = message.split('\n')  # Split the message into lines
        y_text = 10
        for line in lines:
            while font.getsize(line)[0] > 320:  # Reduce font size if the line is too wide
                font_size -= 1
                font = ImageFont.truetype(FONT_PATH, font_size)
            d.text((10, y_text), line, font=font, fill=(255, 255, 255))
            y_text += font.getsize(line)[1] + 5  # Increment y position for the next line with some padding
        img_path = RELATIVE + 'custom_message.jpg'
        img.save(img_path)  # Save the image
        self.disp.show_image(img_path)  # Display the image
        time.sleep(0.5)  # Display the image for half a second

    def display(self, pic):  # Method to display an image
        impath = RELATIVE + pic  # Define the image path
        print("Displaying: ", impath)  # Log the image path
        try:
            img = cv2.imread(impath)  # Read the image using OpenCV
            if img is None:
                raise FileNotFoundError(f"Image not found: {impath}")
            img = cv2.resize(img, (320, 240))  # Resize the image
            cv2.imwrite(impath, img)  # Save the resized image
            self.disp.show_image(impath)  # Display the image
        except Exception as e:
            print(f"Error displaying image: {e}")  # Log any errors

    def clear_memory(self):  # Method to clear all scores and photos
        try:
            # Clear leaderboard file
            open(LEADERBOARD_FILE, 'w').close()
            self.scores = []
            # Delete all top score photos
            for i in range(1, 4):
                photo_path = RELATIVE + f'top_{i}.jpg'
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            self.display_custom_message("Memory cleared!", "black")
        except Exception as e:
            self.get_logger().error(f"Error clearing memory: {e}")

def main():
    GPIO.setmode(GPIO.BCM)  # Set GPIO mode to BCM
    GPIO.setup(6, GPIO.IN)  # Set up front sensor pin
    GPIO.setup(3, GPIO.IN)  # Set up left sensor pin
    GPIO.setup(16, GPIO.IN)  # Set up right sensor pin

    rclpy.init()  # Initialize the ROS 2 client library
    sample_controller = SampleControllerAsync()  # Create an instance of the SampleControllerAsync class

    try:
        rclpy.spin(sample_controller)  # Spin the node to keep it active
    except KeyboardInterrupt:
        pass
    finally:
        sample_controller.destroy_node()  # Destroy the node
        rclpy.shutdown()  # Shutdown the ROS 2 client library
        GPIO.cleanup()  # Clean up GPIO settings

if __name__ == '__main__':
    main()  # Run the main function if this script is executed
