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
    root.title("Draw Picture")

    # Code for the main frame of the Tkinter window

    main_frame = ttk.Frame(root, padding=2)
    main_frame.grid()

    # Instructions for each key

    instructions = "Create a point by clicking"
    label = ttk.Label(main_frame, text=instructions)
    label.grid(columnspan=1, row=0, column=1)

    instructions2 = "Connect the Points"
    label2 = ttk.Label(main_frame, text=instructions2)
    label2.grid(columnspan=1, row=1, column=1)

    instructions3 = "Set Robot Speed"
    label3 = ttk.Label(main_frame, text=instructions3)
    label3.grid(columnspan=1, row=1, column=3)

    instructions4 = "Set Robot Turn Speed"
    label4 = ttk.Label(main_frame, text=instructions4)
    label4.grid(columnspan=1, row=1, column=4)

    instructions5 = "Exit Program"
    label5 = ttk.Label(main_frame, text=instructions5)
    label5.grid(columnspan=1, row=1, column=2)

    instructions6 = "Clear Points"
    label6 = ttk.Label(main_frame, text=instructions6)
    label6.grid(columnspan=1, row=1, column=0)

    # Creating the slider widgets

    speed_slider = Scale(main_frame, from_=0, to=900, orient=HORIZONTAL)
    speed_slider.grid(row=3, column=3)
    speed_slider["command"] = lambda event: send_drive_speed(mqtt_client, speed_slider.get())

    turn_slider = Scale(main_frame, from_=0, to=900, orient=HORIZONTAL)
    turn_slider.grid(row=3, column=4)
    turn_slider["command"] = lambda event: send_turn_speed(mqtt_client, turn_slider.get())
    # Creating the canvas

    canvas = tkinter.Canvas(main_frame, background="lightgray", width=800, height=500)
    canvas.grid(columnspan=5)

    canvas.bind("<Button-1>", lambda event: left_mouse_click(event, mqtt_client, list_box))

    # Creating the buttons

    connect_button = ttk.Button(main_frame, text="Connect")
    connect_button.grid(row=3, column=1)
    connect_button["command"] = lambda: connect_dots(canvas, mqtt_client)
    root.bind('<space>', lambda event: connect_dots(canvas, mqtt_client))

    clear_button = ttk.Button(main_frame, text="Clear")
    clear_button.grid(row=3, column=0)
    clear_button["command"] = lambda: clear(canvas, mqtt_client, list_box)
    root.bind('<e>', lambda event: clear(canvas, mqtt_client, list_box))

    quit_button = ttk.Button(main_frame, text="Quit")
    quit_button.grid(row=3, column=2)
    quit_button["command"] = lambda: quit_program(mqtt_client)
    root.bind('<Escape>', lambda event: quit_program(mqtt_client))

    confirm_song = ttk.Button(main_frame, text="Play Song")
    confirm_song.grid(row=1, column=5, columnspan=1)
    confirm_song["command"] = lambda: pick_song(song, mqtt_client)

    #Code for the Extra frame

    ext_frame = ttk.Frame(main_frame, padding=2)
    ext_frame.grid(row=4, column=6)

    list_box = Listbox(ext_frame, selectmode=EXTENDED)
    list_box.insert(END, "List of points (X, Y)")
    list_box.grid(row=0, column=1, columnspan=1)

    instructions7 = "Change Drive Scale"
    label7 = ttk.Label(ext_frame, text=instructions7)
    label7.grid(columnspan=1, row=1, column=1)

    room_scale = Scale(ext_frame, from_=0, to=20, orient=VERTICAL)
    room_scale.grid(row=0, column=0, columnspan=1)
    room_scale["command"] = lambda event: send_scale(mqtt_client, room_scale.get())

    # Code for drop-down menu

    song = StringVar(main_frame)
    song.set("Pick Song")

    drop_menu = OptionMenu(main_frame, song, "NumberOneShort","NumberOneFull", "MineOn", "AllStar")
    drop_menu.grid(row=0, column=5, columnspan = 1)

    #Sending commands to the delegate

    my_delegate = MyDelegatePC(canvas)
    mqtt_client = com.MqttClient(my_delegate)
    mqtt_client.connect_to_ev3(lego_robot_number=8)

    root.mainloop()

# Function to exit the program
def pick_song(song, mqtt_client):
    if song.get() != "Pick Song":
        print("Now Playing: ", song.get())
        mqtt_client.send_message("play_song", [song.get()])
    else:
        print("Please choose a song")



def quit_program(mqtt_client):
    mqtt_client.close()
    exit()

# Function to draw circles client side, and send coordinates to the delegate
# Also populates a list of all the points to be seen client-side
def left_mouse_click(event, mqtt_client, list_box):
    global points
    """ Draws a circle onto the canvas (one way or another). """
    print("You clicked location ({},{})".format(event.x, event.y))

    points += [(event.x, event.y)]

    list_box.insert(END, points[len(points)-1])

    # Examples... "red", "green", "blue", "yellow", "aquamarine", "magenta", "navy", "orange"
    my_color = "navy"  # Make your color unique

    canvas = event.widget
    canvas.create_oval(event.x - 10, event.y - 10,
                       event.x + 10, event.y + 10,
                       fill=my_color, width=3)

    mqtt_client.send_message("on_circle_draw",[event.x, event.y])

# Clears the list of points client and over the delegate
def clear(canvas, mqtt_client, list_box):
    """Clears the canvas contents"""
    canvas.delete("all")
    mqtt_client.send_message("clear")
    for k in range(len(points)):
        list_box.delete(k+1, END)
    points.clear()

# Tells the robot to "connect the dots" or draw the picture that has been sent using the points
def connect_dots(canvas, mqtt_client):
    if len(points) > 1:
        for k in range(len(points)-1):
            canvas.create_line(points[k][0], points[k][1], points[k+1][0], points[k+1][1], fill="black", dash=(4,2))
        mqtt_client.send_message("connect_dots")
        print("Sent list of points: ", points)

    else:
        print("Error: Invalid number of points. Draw 2 or more points to connect.")

# Sends the drive speed to the delegate using input from the slider
def send_drive_speed(mqtt_client, drive_speed):
    print("Sending drive speed = {}".format(drive_speed))
    mqtt_client.send_message("drive_bot",[drive_speed])
    time.sleep(0.10)

# Sends the turn speed to the delegate using input from the slider
def send_turn_speed(mqtt_client, turn_speed):
    print("Sending turn speed = {}".format(turn_speed))
    mqtt_client.send_message("drive_bot", [turn_speed])
    time.sleep(0.10)

def send_scale(mqtt_client, scale):
    print("Sending scale = {}".format(scale / 100))
    mqtt_client.send_message("change_scale", [scale / 100])
    time.sleep(0.10)

main()

