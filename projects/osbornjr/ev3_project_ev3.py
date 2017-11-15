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
        self.running = False
        self.mqtt_client = None
        self.lcd = ev3.Screen()
        self.scale = 0.05
        self.speed = 100
        self.turn_speed = 100

    def change_scale(self, scale):
        self.scale = scale

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
            if (self.points[k][0] - self.points[k - 1][0]) != 0:
                self.angle = math.atan((self.points[k][1] - self.points[k-1][1]) / (self.points[k][0] - self.points[k-1][0])) * (180 / math.pi)
                robot.turn_degrees(self.angle, self.turn_speed)
            elif (self.points[k][0] - self.points[k - 1][0]) == 0:
                self.angle = 0
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
            if math.sqrt((self.points[k][1] - self.points[k-1][1]) ** 2 + (self.points[k][0] - self.points[k-1][0]) ** 2) * self.scale != 0:
                self.distance = math.sqrt((self.points[k][1] - self.points[k-1][1]) ** 2 + (self.points[k][0] - self.points[k-1][0]) ** 2) * self.scale
                robot.drive_inches(self.distance, self.speed)
            elif math.sqrt((self.points[k][1] - self.points[k-1][1]) ** 2 + (self.points[k][0] - self.points[k-1][0]) ** 2) * self.scale == 0:
                self.distance = 0
            time.sleep(1)
            print("Turn Angle: ", self.angle, "Drive Distance", self.distance)

        print("Final Destination Reached")
        ev3.Sound.speak("Destination Reached").wait()

    def clear(self):
        self.points.clear()

    def loop_forever(self):
        self.running = True

        while not robot.touch_sensor.is_pressed and self.running and robot.ir_sensor.proximity >= 5:
            # Do nothing while waiting for commands

            time.sleep(0.01)
        self.exit()
        # Copied from robot.shutdown

        print("Goodbye")
        ev3.Sound.speak("Goodbye").wait()

    def play_song(self, song):
        self.song = song
        if song == "NumberOneShort":
            self.NumberOne = Image.open("/home/robot/csse120/assets/images/ev3_project_images/WeAreNumberOne.bmp")
            self.lcd.image.paste(self.NumberOne, (0,0))
            self.lcd.update()
            ev3.Sound.play("/home/robot/csse120/assets/sounds/WeAreNumberOne.wav")
        elif song ==  "NumberOneFull":
            self.NumberOne = Image.open("/home/robot/csse120/assets/images/ev3_project_images/WeAreNumberOne.bmp")
            self.lcd.image.paste(self.NumberOne, (0, 0))
            self.lcd.update()
            ev3.Sound.play("/home/robot/csse120/assets/sounds/WeAreNumberOneFull.wav")
        elif song == "MineOn":
            self.MineOn = Image.open("/home/robot/csse120/assets/images/ev3_project_images/MineOn.bmp")
            self.lcd.image.paste(self.MineOn, (0, 0))
            self.lcd.update()
            ev3.Sound.play("/home/robot/csse120/assets/sounds/MineOn.wav")
        elif song == "AllStar":
            self.Shrek = Image.open("/home/robot/csse120/assets/images/ev3_project_images/Shrek.bmp")
            self.lcd.image.paste(self.Shrek, (0, 0))
            self.lcd.update()
            ev3.Sound.play("/home/robot/csse120/assets/sounds/AllStar.wav")
        else:
            print("Error: Unknown song")

    def exit(self):
        self.mqtt_client.close()



def main():
    print("-----------------------------------")
    print("            ev3_project_ev3            ")
    print("-----------------------------------")
    ev3.Sound.speak("ev3_project_ev3").wait()

    my_delegate = MyDelegateEV3()
    mqtt_client = com.MqttClient(my_delegate)
    my_delegate.mqtt_client = mqtt_client
    mqtt_client.connect_to_pc(lego_robot_number=8)

    time.sleep(0.1)
    my_delegate.loop_forever()



main()
