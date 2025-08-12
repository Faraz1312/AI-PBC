from gpiozero import Button
from signal import pause
import os

def shutdown():
    print("Shutdown button pressed. Shutting down...")
    os.system("sudo shutdown -h now")

# Use GPIO pin 26 (BCM mode)
button = Button(26, pull_up=True)

button.when_pressed = shutdown

print("Shutdown button listener running...")
pause()  # Wait indefinitely
