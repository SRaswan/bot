import rclpy
from rclpy.node import Node
from pupper_interfaces.srv import GoPupper
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
from MangDang.mini_pupper.display import Display, BehaviorState
import time
import random
import numpy as np
import cv2
from resizeimage import resizeimage
from PIL import Image as PILImage, ImageDraw, ImageFont
import RPi.GPIO as GPIO

MAX_WIDTH = 320

class PupperGameNode(Node):

    def __init__(self):
        super().__init__('pupper_game_node')
        
        self.cli = self.create_client(GoPupper, 'pup_command')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        
        self.req = GoPupper.Request()
        
        self.sensor_stack = []
        self.current_move_index = 0
        self.awaiting_input = False
        self.timer = self.create_timer(1.0, self.pupper_game)
        self.input_mode = False
        self.game_phase = 0
        
        self.display = Display()
        self.color_sequence = []
        self.color_index = 0
        self.camera_subscription = self.create_subscription(
            Image, '/oak/rgb/image_raw', self.process_camera_input, 10)
        self.publisher_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.br = CvBridge()
        
    def send_move_request(self, idx):
        move_commands = ["move_forward", "move_right", "move_left"]
        self.req.command = move_commands[idx]
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

    def get_user_input(self):
        tFront = GPIO.input(6)
        tLeft = GPIO.input(3)
        tRight = GPIO.input(16)
        if not tFront:
            return 0
        elif not tRight:
            return 1
        elif not tLeft:
            return 2
        return -1

    def perform_sensor_stack_moves(self):
        for move in self.sensor_stack:
            self.send_move_request(move)
            time.sleep(1)

    def display_image(self, imgLoc):
        imgFile = PILImage.open(imgLoc)
        if imgFile.format == 'PNG' and imgFile.mode != 'RGBA':
            imgOld = imgFile.convert("RGBA")
            imgFile = PILImage.new('RGBA', imgOld.size, (255, 255, 255))
        width_size = (MAX_WIDTH / float(imgFile.size[0]))
        imgFile = resizeimage.resize_width(imgFile, MAX_WIDTH)
        newFileLoc = 'img/resized_image.png'
        imgFile.save(newFileLoc, imgFile.format)
        self.display.show_image(newFileLoc)

    def show_color_sequence(self):
        colors = ["red", "green", "blue"]
        color_images = {
            "red": "img/red.png",
            "green": "img/green.png",
            "blue": "img/blue.png"
        }
        new_color = random.choice(colors)
        self.color_sequence.append(new_color)
        print(f"Displaying color sequence: {self.color_sequence}")
        for color in self.color_sequence:
            self.display_image(color_images[color])
            time.sleep(1)

    def process_camera_input(self, data):
        current_frame = self.br.imgmsg_to_cv2(data)
        hsv = cv2.cvtColor(current_frame, cv2.COLOR_BGR2HSV)
        color_masks = {
            "blue": cv2.inRange(hsv, (55, 50, 50), (130, 255, 255)),
            "red": cv2.inRange(hsv, (160, 50, 50), (180, 255, 255)),
            "green": cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))
        }
        color_detected = False
        for color, mask in color_masks.items():
            masked_frame = cv2.bitwise_and(current_frame, current_frame, mask=mask)
            if masked_frame.any() > 0:
                if color == self.color_sequence[self.color_index]:
                    self.color_index += 1
                    if self.color_index >= len(self.color_sequence):
                        print("Correct color sequence! Moving to the next level.")
                        self.color_sequence = []
                        self.color_index = 0
                        self.game_phase = 0
                        self.input_mode = False
                else:
                    print("Incorrect color! Try again.")
                    self.color_sequence = []
                    self.color_index = 0
                    self.game_phase = 0
                    self.input_mode = False
                color_detected = True
                break
        if not color_detected:
            cv2.imshow("Camera Input", current_frame)
            cv2.waitKey(1)

    def pupper_game(self):
        if self.game_phase == 0:
            new_move = random.randint(0, 2)
            self.sensor_stack.append(new_move)
            print(f"Dancing with move {new_move}")
            self.perform_sensor_stack_moves()
            print("New move added to the sequence. Awaiting user input...")
            self.awaiting_input = True
            self.current_move_index = 0
            self.game_phase = 1

        if self.game_phase == 1 and self.awaiting_input:
            response = self.get_user_input()
            if response != -1:
                if response == self.sensor_stack[self.current_move_index]:
                    self.current_move_index += 1
                    print("Nice. keep going")
                    if self.current_move_index >= len(self.sensor_stack):
                        print("Correct! Moving to the next level.")
                        self.send_move_request(self.sensor_stack[-1])
                        self.awaiting_input = False
                        self.game_phase = 2  # Move to the next game phase
                else:
                    print("You failed! Try again.")
                    self.sensor_stack = []
                    self.awaiting_input = False
                    self.game_phase = 0

        if self.game_phase == 2:
            self.show_color_sequence()
            self.input_mode = True
            self.game_phase = 3

        if self.game_phase == 3 and self.input_mode:
            pass  # Color detection handled in process_camera_input

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.IN)
    GPIO.setup(3, GPIO.IN)
    GPIO.setup(16, GPIO.IN)

    rclpy.init()
    game_node = PupperGameNode()

    try:
        rclpy.spin(game_node)
    except KeyboardInterrupt:
        pass
    finally:
        game_node.destroy_node()
        rclpy.shutdown()
        GPIO.cleanup()

if __name__ == '__main__':
    main()
