from pupper_interfaces.srv import GoPupper
import rclpy
from rclpy.node import Node
import time
import RPi.GPIO as GPIO
import random

class SampleControllerAsync(Node):

    def __init__(self):
        super().__init__('sample_controller')
        self.cli = self.create_client(GoPupper, 'pup_command')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')

        self.req = GoPupper.Request()
        self.sensor_stack = []
        self.timer = self.create_timer(1.0, self.pupper)
        self.current_move_index = 0
        self.awaiting_input = False

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

    def pupper(self):
        new_move = random.randint(0, 2)
        self.sensor_stack.append(new_move)

        print("Dancing with" + new_move)

        for move in self.sensor_stack:
            self.send_move_request(move)
            time.sleep(1)
        
        print("New move added to the sequence. Awaiting user input...")
        self.input_mode = True
        self.idx = 0


        while self.input_mode:
            response = self.get_user_input()
            if response != -1:
                if response == self.sensor_stack[self.idx]:
                    self.idx += 1
                    if self.idx >= len(self.sensor_stack):
                        print("Correct! Moving to the next level.")
                        self.send_move_request(self.sensor_stack[-1])
                        self.input_mode = False
                else:
                    print("You failed! Try again.")
                    self.sensor_stack = []
                    self.input_mode = False

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