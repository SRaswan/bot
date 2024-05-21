from pupper_interfaces.srv import GoPupper

from MangDang.mini_pupper.display import Display, BehaviorState
from resizeimage import resizeimage  # library for image resizing
from PIL import Image, ImageDraw, ImageFont # library for image manip.
import rclpy
from rclpy.node import Node
import time
import RPi.GPIO as GPIO
import os.path

class SampleControllerAsync(Node):

    def __init__(self):
        # initalize
        super().__init__('sample_controller')
        self.cli = self.create_client(GoPupper, 'pup_command')

        # Check once per second if service matching the name is available 
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')

        # Create a new request object.
        self.req = GoPupper.Request()


    ###
    # Name: send_move_request
    # Purpose: send_move_request method, send request and spin until receive response or fail
    # Arguments:  self (reference the current class), move_command (the command we plan to send to the server)
    #####
    def send_move_request(self, move_command):
        self.req = GoPupper.Request()
        self.req.command = move_command
        # Debug - uncomment if needed
        print("In send_move_request, command is: %s" % self.req.command)
        self.future = self.cli.call_async(self.req)  # send the command to the server
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

    ###
    # Name: pupper_conga_dance
    # Purpose: Try to make the robot do the Conga (salsa), as per Gloria Estefan. We don't
    #          have a robot choreopgraher here so we'll just do our best.
    # Arguments:  self (reference the current class) -- /not sure if needed, but won't hurt/
    #####
    def pupper_conga_dance(self, GPIO):

        disp = Display()
        imgLoc = "img/h.jpg"

        while True:
            tFront = GPIO.input(6)
        
            tLeft = GPIO.input(3)
            tRight = GPIO.input(16)
            if not tFront:
                imgLoc = "img/h.jpg"
                self.send_move_request("move_forward")
            if not tRight:
                imgLoc = "img/anime.jpg"
                self.send_move_request("move_right")
            if not tLeft:
                imgLoc = "img/Chase-Copy2.jpg"
                self.send_move_request("move_left")
            if tFront and tLeft and tRight:
                self.send_move_request("stay")

            imgFile = Image.open("/home/ubuntu/ros2_ws/src/lab2task4/lab2task4/"+imgLoc)
            

            if (imgFile.format == 'PNG'):
                if (imgFile.mode != 'RGBA'):
                    imgOld = imgFile.convert("RGBA")
                    imgFile = Image.new('RGBA', imgOld.size, (255, 255, 255))

            width_size = (320 / float(imgFile.size[0]))
            imgFile = resizeimage.resize_width(imgFile, 320)

            newFileLoc = '/home/ubuntu/ros2_ws/src/lab2task4/lab2task4/img/animeRZ.png'   #rename as you like

            imgFile.save(newFileLoc, imgFile.format)

            disp.show_image(newFileLoc)
            time.sleep(0.5)
###
# Name: Main
# Purpose: Main function. Going to try to have the robot dance salsa. 
#####
def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(6, GPIO.IN)
    
    GPIO.setup(3, GPIO.IN)
    GPIO.setup(16, GPIO.IN)
    rclpy.init()
    sample_controller = SampleControllerAsync()

    # send commands to do the conga dance
    sample_controller.pupper_conga_dance(GPIO)

    # This spins up a client node, checks if it's done, throws an exception of there's an issue
    # (Probably a bit redundant with other code and can be simplified. But right now it works, so ¯\_(ツ)_/¯)
    while rclpy.ok():
        rclpy.spin(sample_controller)
        if sample_controller.future.done():
            try:
                response = sample_controller.future.result()
            except Exception as e:
                sample_controller.get_logger().info(
                    'Service call failed %r' % (e,))
            else:
                sample_controller.get_logger().info(
                   'Result of command: %s ' %
                   (response))
        break 

    # Destroy node and shut down
    sample_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()


