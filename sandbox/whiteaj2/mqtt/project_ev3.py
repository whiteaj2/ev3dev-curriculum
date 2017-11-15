import robot_controller as robo
import time
import math
import mqtt_remote_method_calls as com
import ev3dev.ev3 as ev3

robot = robo.Snatch3r()
sizeScaler = 10
refresh = 60

mqtt_client = com.MqttClient(robot)
mqtt_client.connect_to_pc(lego_robot_number=8)

class MyDelegate(object):
    def __init__(self):
        self.something = 0
        self.scaler = 10

    def drive_random(self):
        timeDrive = robot.drive_random()
        intervals = timeDrive / refresh
        for k in range(refresh):
            dist = calculate_and_update_distance(robot.left_speed, robot.right_speed, intervals)
            disp = calculate_and_update_position(robot.left_speed, robot.theta, intervals)
            mqtt_client.send_message("robot_move", disp)
            time.sleep(intervals)
        robot.stop()

    def return_home(self):
        robot.theta = math.degrees(math.atan(math.radians(robot.x_pos / robot.y_pos)))
        robot.turn_degrees(robot.theta - 180, 400)
        x_inches = robot.x_pos / sizeScaler
        y_inches = robot.y_pos / sizeScaler
        dist_in_inches = math.sqrt(x_inches ** 2 + y_inches ** 2)
        robot.drive_inches(dist_in_inches, 400)
        robot.turn_degrees(-robot.theta, 400)
        mqtt_client.send_message("robot_move", [0,0])

class DataContainer(object):

    def __init__(self):
        self.running = True


def main():
    newDelegate = MyDelegate()
    mqtt_client.delegate = newDelegate
    mqtt_client.delegate
    mqtt_client.send_message("robot_move", [0, 0])
    dc = DataContainer()
    btn = ev3.Button()

    btn.on_backspace = lambda state: handle_shutdown(state, robot, dc)


    # timer = 0
    #
    # while timer <= 5 and not robot.touch_sensor.is_pressed:
    #     timeDelay = robot.drive_random()
    #     dist = calculate_and_update_distance(robot.left_speed, robot.right_speed, timeDelay)
    #     disp = calculate_and_update_position(robot.left_speed, robot.theta, timeDelay)
    #     time.sleep(timeDelay)
    #     robot.stop()
    #     mqtt_client.send_message("robot_move", disp)
    #     print(dist)
    #     timer += timeDelay
    while dc.running:
        btn.process()
        update_current_color(robot.color_sensor.color)
        time.sleep(0.25)

def handle_shutdown(state, robot, dc):
    if state:
        robot.stop()
        dc.running = False


def calculate_and_update_distance(ls, rs, timeInterval):
    inches_left = ls * (4/360)
    inches_right = rs * (4/360)
    distance_left = inches_left * timeInterval
    distance_right = inches_right * timeInterval
    dist = math.sqrt(distance_left**2 + distance_right**2)
    robot.distance_driven += dist
    return robot.distance_driven

def calculate_and_update_position(speed, theta, timeInterval):
    speed_in_inches = speed * (4/360)
    dist = speed_in_inches * timeInterval
    radTheta = math.radians(theta)
    x_dist = math.sin(radTheta)*dist*sizeScaler
    y_dist = math.cos(radTheta)*dist*sizeScaler
    robot.x_pos += x_dist
    robot.y_pos += y_dist
    return [robot.x_pos, robot.y_pos]

def update_current_color(color):
    colors = ["lightgray", "black", "blue", "green", "yellow", "red", "white", "brown"]
    mqtt_client.send_message("color_update", [colors[color]])



main()