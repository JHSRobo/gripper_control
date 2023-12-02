# This program's purpose is to provide software control of the grippers
# In the TCU, we have a Phidget controller.
# This program recognizes an "active gripper", whichever gripper is in view of cameras.
# Pressing the gripper button activates this gripper.

# Written by James Randall '24

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from core.msg import Cam

from Phidget22.Phidget import *
from Phidget22.Devices.DigitalOutput import *

# This is the class that ROS2 spins up as a node
class GripperController(Node):

    def __init__(self):
        super().__init__('motion_control')
        
        self.log = self.get_logger() # Quick reference for logging

        # Create sub for getting the gripper in frame of the camera
        self.camera_sub = self.create_subscription(Cam, "active_camera", self.cam_callback, 10)
        # Create subscriber for monitoring joystick button presses
        self.joy_sub = self.create_subscription(Joy, 'joy', self.joy_callback, 10)

        self.active_gripper = None
        self.cached_input = False

        self.gripper = { "Front": None, "Bottom": None }

        # Create digital outputs
        self.gripper["Front"] = DigitalOutput()
        self.gripper["Front"].setDeviceSerialNumber(656370)
        self.gripper["Front"].setChannel(0)
        self.gripper["Front"].openWaitForAttachment(3000)

        self.gripper["Bottom"] = DigitalOutput()
        self.gripper["Bottom"].setDeviceSerialNumber(656370)
        self.gripper["Bottom"].setChannel(1)
        self.gripper["Bottom"].openWaitForAttachment(3000)


    def cam_callback(self, cam_msg):
        self.active_gripper = cam_msg.gripper


    def joy_callback(self, joy_msg):
        # Enable or disable active gripper based on button press
        if joy_msg.buttons[0] and not self.cached_input:
            self.toggle_gripper()
        self.cached_input = joy_msg.buttons[0]


    def toggle_gripper(self):
        # Get active gripper
        gripper = self.gripper[self.active_gripper]

        if gripper.getDutyCycle() == 1:
            gripper.setDutyCycle(0)
        elif not gripper.getDutyCycle() == 0:
            gripper.setDutyCycle(1)


    def exit_grippers(self):
        self.gripper["Front"].close()
        self.gripper["Bottom"].close()


def main(args=None):
    rclpy.init(args=args)

    gripper_controller = GripperController()

    # Runs the program until shutdown is recieved
    rclpy.spin(gripper_controller)

    # On shutdown, kill node
    gripper_controller.exit_grippers()
    gripper_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()