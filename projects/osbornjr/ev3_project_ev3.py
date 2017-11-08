import ev3dev.ev3 as ev3
import time
import robot_controller as robo
import mqtt_remote_method_calls as com
import math

robot = robo.Snatch3r()


class MyDelegateEV3(object):

    def __init__(self):
        self.points = []
        self.running = True
        self.mqtt_client = None
        self.lcd = ev3.Screen()
        self.scale = 0.10

    def drive_bot(self, speed):
        self.speed = speed

    def on_circle_draw(self, x, y):

        self.x = x
        self.y = y
        self.points += [(x,y)]
        print(self.points)

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

    def connect_dots(self):
        self.angle = math.atan((self.points[1][1] - self.points[0][1]) / (self.points[1][0] - self.points[0][0])) * (180 / math.pi)
        robot.turn_degrees(self.angle, 100)
        time.sleep(1)
        self.distance = math.sqrt((self.points[1][1] - self.points[0][1]) ** 2 + (self.points[1][0] - self.points[0][0]) ** 2) * self.scale
        robot.drive_inches(self.distance, self.speed)

    def clear(self):
        self.points.clear()

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
