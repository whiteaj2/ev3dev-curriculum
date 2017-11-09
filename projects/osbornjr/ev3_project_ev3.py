import ev3dev.ev3 as ev3
import time
import robot_controller as robo
import mqtt_remote_method_calls as com
import math
from PIL import Image

robot = robo.Snatch3r()


class MyDelegateEV3(object):

    def __init__(self):
        self.points = []
        self.running = True
        self.mqtt_client = None
        self.lcd = ev3.Screen()
        self.scale = 0.05

    def drive_bot(self, speed):
        self.speed = speed

    def turn_bot(self, turn_speed):
        self.turn_speed = turn_speed

    def on_circle_draw(self, x, y):

        self.x = x
        self.y = y
        self.points += [(x,y)]
        print(self.points)

    def connect_dots(self):
        for k in range(len(self.points)-1):
            self.angle = math.atan((self.points[k][1] - self.points[k-1][1]) / (self.points[k][0] - self.points[k-1][0])) * (180 / math.pi)
            robot.turn_degrees(self.angle, self.turn_speed)
            if self.angle < 180:
                print("Left turn neccesary")
                ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.GREEN)
                ev3.Leds.set_color(ev3.Leds.RIGHT, ev3.Leds.RED)
            elif self.angle > 180:
                print("Right turn neccesary")
                ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.RED)
                ev3.Leds.set_color(ev3.Leds.RIGHT, ev3.Leds.GREEN)
            else:
                print("No turn neccesary")
                ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.AMBER)
                ev3.Leds.set_color(ev3.Leds.RIGHT, ev3.Leds.AMBER)
            time.sleep(1)
            self.distance = math.sqrt((self.points[k][1] - self.points[k-1][1]) ** 2 + (self.points[k][0] - self.points[k-1][0]) ** 2) * self.scale
            robot.drive_inches(self.distance, self.speed)
            time.sleep(1)
            print("Turn Angle: ", self.angle, "Drive Distance", self.distance)
        print("Final Destination Reached")
        ev3.Sound.speak("Destination Reached").wait()

    def clear(self):
        self.points.clear()

def main():
    print("-----------------------------------")
    print("            ev3_project_ev3            ")
    print("-----------------------------------")
    ev3.Sound.speak("ev3_project_ev3").wait()

    while not robot.touch_sensor.is_pressed:

        my_delegate = MyDelegateEV3()
        mqtt_client = com.MqttClient(my_delegate)
        mqtt_client.connect_to_pc(lego_robot_number=8)

        WeAreNumberOne = Image.open("/home/robot/csse120/assets/images/ev3_project_images/WeAreNumberOne.bmp")
        my_delegate.lcd.image.paste(WeAreNumberOne, (0, 0))
        my_delegate.lcd.update()

        ev3.Sound.play("/home/robot/csse120/assets/sounds/WeAreNumberOne.wav")

        time.sleep(0.1)

    print("Goodbye")
    ev3.Sound.speak("Goodbye").wait()

main()
