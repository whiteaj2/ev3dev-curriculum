#!/usr/bin/env python3
"""
The goal of this module is to practice using the Pixy and MQTT at the same time.  This module will send data from the
EV3 to the PC.

Authors: David Fisher and Joshua Osborne.  February 2017.
"""  # Done: 1. PUT YOUR NAME IN THE ABOVE LINE.

import ev3dev.ev3 as ev3
import time

import robot_controller as robo
import mqtt_remote_method_calls as com


def main():
    print("--------------------------------------------")
    print(" Pixy display")
    print(" Press the touch sensor to exit")
    print("--------------------------------------------")
    ev3.Sound.speak("Pixy display").wait()
    print("Press the touch sensor to exit this program.")

    # TODO: 2. Create an MqttClient (no delegate needed since EV3 will only send data, so an empty constructor is fine)
    # Then connect to the pc using the connect_to_pc method.
    mqtt_client = com.MqttClient()
    mqtt_client.connect_to_pc(lego_robot_number=8)

    print("1")
    robot = robo.Snatch3r()
    print("2")
    pixy1 = robot.pixy
    print("3")
    pixy1.mode = "SIG1"

    while not robot.touch_sensor.is_pressed:
        # TODO: 3. Read the Pixy values for x, y, width, and height
        # Print the values (much like the print_pixy_readings example)
        print("value1: X", pixy1.value(1))
        print("value2: Y", pixy1.value(2))
        print("value3: Width", pixy1.value(3))
        print("value4: Height", pixy1.value(4))


        # TODO: 4. Send the Pixy values to the PC by calling the on_rectangle_update method
        # If you open m2_pc_pixy_display you can see the parameters for that method [x, y, width, height]
        mqtt_client.send_message("on_rectangle_update", [pixy1.value(1),pixy1.value(2),pixy1.value(3),pixy1.value(4)])



        time.sleep(0.25)

    print("Goodbye!")
    ev3.Sound.speak("Goodbye").wait()
    mqtt_client.close()

# TODO: 5. Call over a TA or instructor to sign your team's checkoff sheet.
#
# Observations you should make, if the EV3 has data the PC can know that data too using MQTT.


# ----------------------------------------------------------------------
# Calls  main  to start the ball rolling.
# ----------------------------------------------------------------------
main()

