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

            self.active_gripper = None
            self.cached_input = [False, False]

            self.gripper = { "Front": None, "Bottom": None }

            try:
                # Create digital outputs
                self.gripper["Front"] = DigitalOutput()
                self.gripper["Front"].setChannel(0)
                self.gripper["Front"].openWaitForAttachment(3000)

                self.gripper["Bottom"] = DigitalOutput()
                self.gripper["Bottom"].setChannel(1)
                self.gripper["Bottom"].openWaitForAttachment(3000)
            except:
                self.log.warn("Could not connect to grippers. Ignore this if Phidget is unplugged")
            else:
                # Create sub for getting the gripper in frame of the camera
                self.camera_sub = self.create_subscription(Cam, "active_camera", self.cam_callback, 10)
                # Create subscriber for monitoring joystick button presses
                self.joy_sub = self.create_subscription(Joy, 'joy', self.joy_callback, 10)


    def cam_callback(self, cam_msg):
        self.active_gripper = cam_msg.gripper


    def joy_callback(self, joy_msg):
        # Enable or disable active gripper based on button press
        if joy_msg.buttons[0] and not self.cached_input[0]:
            self.toggle_gripper()
        if joy_msg.buttons[9] and not self.cached_input[1]:
            self.toggle_secondary_gripper()

        self.cached_input[0] = joy_msg.buttons[0]
        self.cached_input[1] = joy_msg.buttons[8]


    def toggle_gripper(self):
        if self.active_gripper is None:
            self.log.warn("No currently registered active gripper. Defaulting to Front.")
            self.active_gripper = "Front"

        # Get active gripper
        gripper = self.gripper[self.active_gripper]

        if gripper.getDutyCycle():
            gripper.setDutyCycle(0)
            self.log.info("{} gripper opened".format(self.active_gripper))
        elif not gripper.getDutyCycle():
            gripper.setDutyCycle(1)
            self.log.info("{} gripper closed".format(self.active_gripper))
        else:
            self.log.info(str(gripper.getDutyCycle()))

    def toggle_secondary_gripper(self):
        if self.active_gripper == "Front":
            gripper = self.gripper["Bottom"]
        else:
            gripper = self.gripper["Front"]
        if gripper.getDutyCycle():
            gripper.setDutyCycle(0)
            self.log.info("{} gripper opened".format(self.active_gripper))
        elif not gripper.getDutyCycle():
            gripper.setDutyCycle(1)
            self.log.info("{} gripper closed".format(self.active_gripper))
        else:
            self.log.info(str(gripper.getDutyCycle()))


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
