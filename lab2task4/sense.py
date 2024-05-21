
from pupper_interfaces.srv import GoPupper

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
import time
class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')

        self.srv = self.create_service(GoPupper, 'pup_command', self.pup_callback)
        
        self.vel_publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)

        self.interval = 0.5  # .5 seconds


    def pup_callback(self, request, response):
        velocity_cmd = Twist()

        if (request.command == 'move_forward'):
            velocity_cmd.linear.x = 0.5    # .5 in the linear X direction moves us forward
            self.vel_publisher_.publish(velocity_cmd)   # publish the command
            self.get_logger().info('Publishing: "%s"' % request.command)  # Log what happened
            time.sleep(self.interval)  # Wait and make sure the robot moved

        elif (request.command == 'move_backward'):
            velocity_cmd.linear.x = -0.5
            self.vel_publisher_.publish(velocity_cmd)
            self.get_logger().info('Publishing: "%s"' % request.command)
            time.sleep(self.interval)   

        elif (request.command == 'move_left'):
            velocity_cmd.linear.y = 0.5
            self.vel_publisher_.publish(velocity_cmd)
            self.get_logger().info('Publishing: "%s"' % request.command)
            time.sleep(self.interval)   

        elif (request.command == 'move_right'):
            velocity_cmd.linear.y = -0.5
            self.vel_publisher_.publish(velocity_cmd)
            self.get_logger().info('Publishing: "%s"' % request.command)
            time.sleep(self.interval)   

        elif (request.command == 'turn_left'):
            velocity_cmd.angular.z = 1.0
            self.vel_publisher_.publish(velocity_cmd)
            self.get_logger().info('Publishing: "%s"' % request.command)
            time.sleep(self.interval)  

        elif (request.command == 'turn_right'):
            velocity_cmd.angular.z = -1.0
            self.vel_publisher_.publish(velocity_cmd)
            self.get_logger().info('Publishing: "%s"' % request.command)
            time.sleep(self.interval)   
    
        elif (request.command == 'stay'):
            time.sleep(self.interval)  # do nothing

        else:
            self.get_logger().info('Invalid command: "%s"' % request.command)
            time.sleep(self.interval)  # do nothing

        velocity_cmd = Twist()
        self.vel_publisher_.publish(velocity_cmd)

        response.executed = True
        return response

####
# Name: Main
# Purpose: Main functoin to set up our service
#####
def main():
    # Initialize the python client library in ROS 2
    rclpy.init()

    # Instatiate the class & create the node for the service
    minimal_service = MinimalService()

    # Spin the node - this will handle call backs
    rclpy.spin(minimal_service)

    # Destroy the node when we're done with it
    minimal_service.destroy_node()
    
    # Shutdown  
    rclpy.shutdown()


if __name__ == '__main__':
    main()
