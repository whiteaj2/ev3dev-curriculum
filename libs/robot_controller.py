"""
  Library of EV3 robot functions that are useful in many different applications. For example things
  like arm_up, arm_down, driving around, or doing things with the Pixy camera.

  Add commands as needed to support the features you'd like to implement.  For organizational
  purposes try to only write methods into this library that are NOT specific to one tasks, but
  rather methods that would be useful regardless of the activity.  For example, don't make
  a connection to the remote control that sends the arm up if the ir remote control up button
  is pressed.  That's a specific input --> output task.  Maybe some other task would want to use
  the IR remote up button for something different.  Instead just make a method called arm_up that
  could be called.  That way it's a generic action that could be used in any task.
"""

import ev3dev.ev3 as ev3
import math
import time
import random


class Snatch3r(object):
    """Commands for the Snatch3r robot that might be useful in many different programs."""
    
    # DONE: Implement the Snatch3r class as needed when working the sandbox exercises
    # (and delete these comments)
    def __init__(self):
        # Connect two large motors on output ports B and C
        self.left_motor = ev3.LargeMotor(ev3.OUTPUT_B)
        self.right_motor = ev3.LargeMotor(ev3.OUTPUT_C)
        self.arm_motor = ev3.MediumMotor(ev3.OUTPUT_A)
        self.touch_sensor = ev3.TouchSensor()
        self.left_led = ev3.Leds.LEFT
        self.right_led = ev3.Leds.RIGHT
        self.color_sensor = ev3.ColorSensor()
        self.ir_sensor = ev3.InfraredSensor()
        self.pixy = ev3.Sensor(driver_name="pixy-lego")
        self.left_speed = 0
        self.right_speed = 0
        #Theta is the angle the front of the robot makes with the left vertical on the screen
        self.theta = 0
        self.x_pos = 0
        self.y_pos=0
        self.distance_driven = 0

        # Check that the motors are actually connected
        assert self.left_motor.connected
        assert self.right_motor.connected
        assert self.arm_motor.connected
        assert self.touch_sensor.connected
        assert self.color_sensor
        assert self.ir_sensor
        assert self.pixy.connected

        self.running = None

    def drive_inches(self, distance, sp):
        """Drives the robot a given number of inches at a given speed"""
        ev3.Sound.speak("Driving")
        self.left_motor.run_to_rel_pos(position_sp=distance*90, speed_sp=sp)
        self.right_motor.run_to_rel_pos(position_sp=distance * 90, speed_sp=sp)
        self.left_speed = sp
        self.right_speed = sp
        self.left_motor.wait_while(self.left_motor.STATE_RUNNING)
        self.right_motor.wait_while(self.right_motor.STATE_RUNNING)
        self.left_speed = 0
        self.right_speed = 0
        ev3.Sound.beep().wait()

    def turn_degrees(self, degrees_to_turn, turn_speed_sp):
        """Turns the robot a given number of degrees( left is positive, right is negative )"""
        ev3.Sound.speak("Turning")
        self.left_motor.run_to_rel_pos(position_sp=-4*1.24*degrees_to_turn, speed_sp=turn_speed_sp)
        self.right_motor.run_to_rel_pos(position_sp=4*1.24*degrees_to_turn, speed_sp=turn_speed_sp)
        self.left_motor.wait_while(self.left_motor.STATE_RUNNING)
        self.right_motor.wait_while(self.right_motor.STATE_RUNNING)
        self.theta += degrees_to_turn
        ev3.Sound.beep().wait()

    def arm_calibration(self):
        self.arm_motor.run_forever(speed_sp=900)
        print("Going up")
        while not self.touch_sensor.is_pressed:
            time.sleep(0.01)
        self.arm_motor.stop(stop_action="brake")

        print("Going down")
        self.arm_motor.run_to_rel_pos(position_sp=-14.2 * 360)
        self.arm_motor.wait_while(self.arm_motor.STATE_RUNNING)
        ev3.Sound.beep().wait()
        self.arm_motor.position = 0

    def arm_up(self):
        self.arm_motor.run_forever(speed_sp=900)
        while not self.touch_sensor.is_pressed:
            time.sleep(0.01)
        self.arm_motor.stop(stop_action="brake")
        ev3.Sound.beep().wait()

    def arm_down(self):
        self.arm_motor.run_to_abs_pos(position_sp=0, speed_sp=900)
        self.arm_motor.wait_while(self.arm_motor.STATE_RUNNING)
        ev3.Sound.beep().wait()

    def shutdown(self):
        self.left_motor.stop(stop_action="brake")
        self.right_motor.stop(stop_action="brake")
        ev3.Leds.set_color(self.left_led, ev3.Leds.GREEN)
        ev3.Leds.set_color(self.right_led, ev3.Leds.GREEN)

        self.running = False

    def loop_forever(self):
        self.running = True
        while self.running:
            time.sleep(0.01)

    def drive(self, left_motor_speed, right_motor_speed):
        self.left_motor.run_forever(speed_sp=left_motor_speed)
        self.right_motor.run_forever(speed_sp=right_motor_speed)
        self.left_speed = left_motor_speed
        self.right_speed = right_motor_speed

    def stop(self):
        #turns off motors
        self.left_motor.stop(stop_action="brake")
        self.right_motor.stop(stop_action="brake")
        self.left_speed = 0
        self.right_speed = 0

    def drive_random(self):
        #Drives for a random amount of time at a random speed
        #Returns the time driven in order to calculate the distance travelled
        turn_degrees = random.randrange(0, 30)
        speed = random.randrange(200,801)
        rand_time = random.randrange(1,4)
        self.turn_degrees(turn_degrees, 400)
        self.drive(speed, speed)
        self.left_speed = speed
        self.right_speed = speed
        return rand_time


    def seek_beacon(self, beacon_channel, forward_speed, turn_speed):
        beacon_seeker = ev3.BeaconSeeker(channel=beacon_channel)
        while not self.touch_sensor.is_pressed:
            current_heading = beacon_seeker.heading
            current_distance = beacon_seeker.distance
            if current_distance == -128:
                # If the IR Remote is not found just sit idle for this program until it is moved.
                print("IR Remote not found. Distance is -128")
                self.stop()
            else:

                if math.fabs(current_heading) < 2:
                    # Close enough of a heading to move forward
                    print("On the right heading. Distance: ", current_distance)
                    # You add more!
                    if current_distance <= 0:
                        self.stop()
                        return True
                    elif current_distance > 0:
                        self.drive(forward_speed, forward_speed)
                        time.sleep(0.10)
                elif math.fabs(current_heading) >= 2 and math.fabs(current_heading) <= 10:
                    print("Spinning to get the right heading. Distance: ", current_distance)
                    if current_heading < 0:
                        print("Heading is too far to the right. Distance: ", current_distance)
                        self.drive(-turn_speed, turn_speed)
                        time.sleep(0.01)
                    elif current_heading > 0:
                        print(" Heading is too far to the left. Distance: ", current_distance)
                        time.sleep(0.01)
                        self.drive(turn_speed, -turn_speed)
                else:
                    print("No IR sensor found in acceptable heading range.")

            time.sleep(0.1)
        print("Touch sensor Pressed, Aborting")
        self.stop()
        return False