import tkinter
import math
from tkinter import ttk
import mqtt_remote_method_calls as com

class MyDelegate(object):

    def __init__(self, canvas, color_canvas):
        self.canvas = canvas
        self.robot_icon = None
        self.color_canvas = color_canvas
        self.rect = None

    def on_circle_draw(self, color, x, y):
        self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill_color=color)

    def print_dist(self, dist):
        print(dist)

    def robot_move(self, x_pos, y_pos):
        self.canvas.delete(self.robot_icon)
        self.robot_icon = self.canvas.create_oval(x_pos - 10, y_pos - 10, x_pos + 10, y_pos + 10, fill='red', width=3)

    def color_update(self, color):
        self.color_canvas.delete(self.rect)
        self.rect = self.color_canvas.create_rectangle(0, 0, 110, 110, fill=color, width=0)



class DataContainer(object):

    def __init__(self):
        self.moves = []

dc = DataContainer()

root = tkinter.Tk()
root.title = "Draw Circles"

main_frame = ttk.Frame(root, padding=5)
main_frame.grid()

text = "Robo-Tracker"
label = ttk.Label(main_frame, text=text)
label.grid(columnspan=2)

canvas = tkinter.Canvas(main_frame, background="darkgray", width=800, height=500)
canvas.grid(columnspan=2)


color_label = ttk.Label(main_frame, text="Current color")
color_label.grid(row=2,column=3)
colorcanvas = tkinter.Canvas(main_frame, background="black", width=100, height=100)
colorcanvas.grid(row=3, column=3)

my_delegate = MyDelegate(canvas, colorcanvas)
mqtt_client = com.MqttClient(my_delegate)
mqtt_client.connect_to_ev3(lego_robot_number=8)

canvas.bind("<Button-1>", lambda event: left_mouse_click(event, mqtt_client))

def main():

    quit_button = ttk.Button(main_frame, text="Quit")
    quit_button.grid(row=0, column = 3)
    quit_button["command"] = lambda: quit_program(mqtt_client)

    random_drive_button = ttk.Button(main_frame, text="Drive Random")
    random_drive_button.grid(row=1, column=3)
    random_drive_button["command"] = lambda: random_drive_handle()

    return_home_button = ttk.Button(main_frame, text="Return Home")
    return_home_button.grid(row=3, column=0)
    return_home_button["command"] = lambda: return_home_handle()

    root.mainloop()

def left_mouse_click(event, mqtt_client):
    canvas.create_oval(event.x - 10, event.y - 10, event.x + 10, event.y + 10, fill='orange', width=3)
    dc.moves.append([event.x, event.y])
    print(dc.moves)

def on_slide(scale):
    print(scale)

def quit_program(mqtt_client):
    if mqtt_client:
        mqtt_client.close()
    exit()

def random_drive_handle():
    mqtt_client.send_message("drive_random", [])

def return_home_handle():
    mqtt_client.send_message("return_home", [])

main()
