import ev3dev.ev3 as ev3
import time
import robot_controller as robo
import mqtt_remote_method_calls as com
import tkinter
from tkinter import ttk

robot = robo.Snatch3r()

global points
points = []

class MyDelegateEV3(object):

    def __init__(self):
        self.running = True
        self.mqtt_client = None
        self.lcd = ev3.Screen()

    def drive_bot(self, speed):
        self.speed = speed
        robot.drive(speed, speed)

    def on_circle_draw(self, x, y):
        self.x = x
        self.y = y
        points += [(x,y)]
        print(points)

    def loop_forever(self):
        btn = ev3.Button()
        self.running = True
        while not btn.backspace and self.running:
            # Do nothing while waiting for commands
            time.sleep(0.01)
        self.mqtt_client.close()
        # Copied from robot.shutdown
        print("Goodbye")
        ev3.Sound.speak("Goodbye").wait()



def main():
    print("-----------------------------------")
    print("            ev3_project_ev3            ")
    print("-----------------------------------")
    ev3.Sound.speak("ev3_project_ev3").wait()

    my_delegate = MyDelegateEV3()
    mqtt_client = com.MqttClient(my_delegate)
    mqtt_client.connect_to_pc(lego_robot_number=8)

    my_delegate.loop_forever()

main()
