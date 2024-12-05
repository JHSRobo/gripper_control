![Image](./img/logo.png)

12/3/24 Version 1.0:


**Contributors:** Jack Frings '26

**Editors:** Jack Frings '26 

**Approved by:** Pending

---
This repository contains the software to control the grippers on the ROV. As our grippers are controlled via pneumatics, we use Phidgets as a relay to open and close both the front and bottom grippers as well as any needed mission tools. When running topside, the grippers node receives a gripper number from [pilot_gui](https://github.com/jhsrobo/pilot_gui). At the same time, the gripper node also checks the joystick input from the pilot. When the pilot presses the trigger on the Hotas joystick, the gripppers node will either open or close whatever gripper is correlated to the current camera. 
