from pupper_interfaces.srv import GoPupper
from MangDang.mini_pupper.display import Display, BehaviorState
import rclpy
from rclpy.node import Node
import time
import RPi.GPIO as GPIO
import random
from resizeimage import resizeimage  # library for image resizing
from PIL import Image, ImageDraw, ImageFont # library for image manip.

RELATIVE = "/home/ubuntu/ros2_ws/src/lab2task4/lab2task4/img/"
MOVES = ["move_forward", "move_right", "move_left"]
COLORS = ["red", "green", "blue"]
class SampleControllerAsync(Node):

    def __init__(self):
        super().__init__('sample_controller')
        self.cli = self.create_client(GoPupper, 'pup_command')
        self.subscription = self.create_subscription(Image, '/oak/rgb/image_raw', self.pupper, 10)

		self.br = CvBridge()

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        
        self.req = GoPupper.Request()
        self.sensor_stack = []
        self.idx = 0
        self.phase = 0
        self.score = 0
        self.timer = self.create_timer(1.0, self.pupper)

    def send_move_request(self, idx):
        self.req = GoPupper.Request()
        self.req.command = MOVES[idx]
        self.future = self.cli.call_async(self.req)
        # rclpy.spin_until_future_complete(self, self.future)
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

    def pupper(self, data):
        print("Phase ", self.phase)
        # Phase 0: Choosing move
        if self.phase == 0:
            print("Pick Move")
            new_move = random.randint(0, 2)
            self.sensor_stack.append(new_move)
            print("Added move ", new_move)
            self.phase = 1
            self.idx = 0

        # Phase 1: Choosing move
        if self.phase == 1:
            print("Dancing")
            if self.idx < len(self.sensor_stack):
                self.send_move_request(self.sensor_stack[self.idx])
                self.idx += 1
            else:
                self.phase = 2
                self.idx = 0
    
        # Phase 2: Sensing
        if self.phase == 2:
            print("Response")
            response = self.get_user_input()
            if response != -1:
                if response == self.sensor_stack[self.idx]:
                    self.idx += 1
                    self.score += 1
                    self.display(MOVES[response])
                    print("Nice! Keep going")
                    if self.idx >= len(self.sensor_stack):
                        print("Correct! Moving to the next level.")
                        self.phase = 0
                else:
                    print("You failed! Try again.")
                    self.sensor_stack = []
                    self.phase = 3
    
        if self.phase == 3:
            print("Pick Color")
            new_color = random.randint(0, 2)
            self.sensor_stack.append(new_color)
            print("Added color ", new_color)
            self.phase = 4
            self.idx = 0
        
        if self.phase == 4:
            print("Show Color")
            if self.idx < len(self.sensor_stack):
                self.display(COLORS[self.sensor_stack[self.idx]])
                self.idx += 1
            else:
                self.phase = 5
                self.idx = 0

        if self.phase == 5:
            print("Response")
            current_frame = self.br.imgmsg_to_cv2(data)
            hsv = cv2.cvtColor(current_frame, cv2.COLOR_BGR2HSV)

            blue_mask = cv2.inRange(hsv, (55, 50, 50), (130, 255, 255))
            red_mask = cv2.inRange(hsv, (160, 50, 50), (180, 255, 255))
            green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))

            blue_masked_frame = cv2.bitwise_and(current_frame, current_frame, mask=blue_mask)
            red_masked_frame = cv2.bitwise_and(current_frame, current_frame, mask=red_mask)
            green_masked_frame = cv2.bitwise_and(current_frame, current_frame, mask=green_mask)       
            cols = [blue_masked_frame, red_masked_frame, green_masked_frame]

            if cv2.countNonZero(cols[self.sensor_stack[self.idx]]) > 15:
                self.idx += 1
                self.score += 1
                print("Nice! Keep going")
                if self.idx >= len(self.sensor_stack):
                    print("Correct! Moving to the next level.")
                    self.phase = 3
            else if cv2.countNonZero(blue_masked_frame) > 15 or cv2.countNonZero(red_masked_frame) > 15 or cv2.countNonZero(green_masked_frame) > 15:
                print("You failed! Try again.")
                self.sensor_stack = []
                self.phase = 6

        # Phase 3: Picture
        if self.phase == 6:
            print("Picture")
            current_frame = self.br.imgmsg_to_cv2(data)
            cv2.imwrite(RELATIVE+"pic.jpg", current_frame)
            self.display("pic.jpg")

    def display(self, pic):
        impath = RELATIVE+pic
        disp = Display()
        imgFile = Image.open(impath)
        width_size = (320 / float(imgFile.size[0]))
        imgFile = resizeimage.resize_width(imgFile, 320)
        imgFile.save(impath, imgFile.format)
        disp.show_image(impath)
        imgFile.close()


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.IN)
    GPIO.setup(3, GPIO.IN)
    GPIO.setup(16, GPIO.IN)

    rclpy.init()
    sample_controller = SampleControllerAsync()

    try:
        rclpy.spin(sample_controller)
    except KeyboardInterrupt:
        pass
    finally:
        sample_controller.destroy_node()
        rclpy.shutdown()
        GPIO.cleanup()

if __name__ == '__main__':
    main()