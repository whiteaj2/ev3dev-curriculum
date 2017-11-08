import ev3dev.ev3 as ev3
import time
import robot_controller as robo
import mqtt_remote_method_calls as com
import tkinter
from tkinter import ttk
from tkinter import *

points = []

# Sends commands through the delegate
class MyDelegatePC(object):

    def __init__(self, canvas, *label_to_display_messages_in):
        self.canvas = canvas
        self.display_label = label_to_display_messages_in

    def on_circle_draw(self, color, x, y):
        print("Received: {},  {} {}".format(color, x, y))
        self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=color, width = 3)



# Main body of code
def main():
    print("-----------------------------------")
    print("            ev3_project_pc            ")
    print("-----------------------------------")

    root = tkinter.Tk()
    root.title = "Draw Picture"

    main_frame = ttk.Frame(root, padding=2)
    main_frame.grid()

    instructions = "Click the window to make a point."
    label = ttk.Label(main_frame, text=instructions)
    label.grid(columnspan=2, row=0, column=1)

    instructions2 = "Click connect to connect the points"
    label2 = ttk.Label(main_frame, text=instructions2)
    label2.grid(columnspan=2, row=1, column=1)

    instructions3 = "Slide the slider for speed"
    label3 = ttk.Label(main_frame, text=instructions3)
    label3.grid(columnspan=2, row=1, column=4)

    speed_slider = Scale(main_frame, from_=0, to=900, orient=HORIZONTAL)
    speed_slider.grid(row=3, column=4)
    speed_slider["command"] = lambda event: send_drive_command(mqtt_client, speed_slider.get())

    canvas = tkinter.Canvas(main_frame, background="lightgray", width=800, height=500)
    canvas.grid(columnspan=5)

    canvas.bind("<Button-1>", lambda event: left_mouse_click(event, mqtt_client))

    connect_button = ttk.Button(main_frame, text="Connect")
    connect_button.grid(row=3, column=1)
    connect_button["command"] = lambda: connect_dots(canvas, mqtt_client)

    clear_button = ttk.Button(main_frame, text="Clear")
    clear_button.grid(row=3, column=0)
    clear_button["command"] = lambda: clear(canvas)

    quit_button = ttk.Button(main_frame, text="Quit")
    quit_button.grid(row=3, column=2)
    quit_button["command"] = lambda: quit_program(mqtt_client)

    my_delegate = MyDelegatePC(canvas)
    mqtt_client = com.MqttClient(my_delegate)
    mqtt_client.connect_to_ev3(lego_robot_number=8)

    root.mainloop()

# Function to exit the program
def quit_program(mqtt_client):
    mqtt_client.close()
    exit()

def left_mouse_click(event, mqtt_client):
    global points
    """ Draws a circle onto the canvas (one way or another). """
    print("You clicked location ({},{})".format(event.x, event.y))

    points += [(event.x, event.y)]

    # Examples... "red", "green", "blue", "yellow", "aquamarine", "magenta", "navy", "orange"
    my_color = "navy"  # Make your color unique

    canvas = event.widget
    canvas.create_oval(event.x - 10, event.y - 10,
                       event.x + 10, event.y + 10,
                       fill=my_color, width=3)

    mqtt_client.send_message("on_circle_draw",[event.x, event.y])


def clear(canvas):
    """Clears the canvas contents"""
    canvas.delete("all")
    points.clear()

def connect_dots(canvas, mqtt_client):
    if len(points) > 1:
        for k in range(len(points)-1):
            mqtt_client.send_message("connect_dots", [points[k][0], points[k][1], points[k+1][0], points[k+1][1]])
            canvas.create_line(points[k][0], points[k][1], points[k+1][0], points[k+1][1], fill="black", dash=(4,2))
        print(points)

    else:
        print("Error: Invalid number of points. Draw 2 or more points to connect.")

def send_drive_command(mqtt_client, drive_speed):
    print("Sending drive speed = {}".format(drive_speed))
    mqtt_client.send_message("drive_bot",[drive_speed])


main()

