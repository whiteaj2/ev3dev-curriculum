import ev3dev.ev3 as ev3
import time

def main():
    print("-----------------------------------")
    print("            ev3_project            ")
    print("-----------------------------------")

    ev3.Sound.speak("ev3_project").wait()

    # Connect two large motors on output ports B and C
    left_motor = ev3.LargeMotor(ev3.OUTPUT_B)
    right_motor = ev3.LargeMotor(ev3.OUTPUT_C)

    # Check that the motors are actually connected
    assert left_motor.connected
    assert right_motor.connected

    # Displays a list of commands for a motor
    print("Motor commands:", left_motor.commands)


main()
