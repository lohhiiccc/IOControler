from IOController import Controller
import time
import math

class MouseMovementUtils:
    def __init__(self, controller):
        self.controller = controller

    def DrawCircle(self, timer, rad, steps, x, y):
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            x2 = int(x + rad * math.cos(angle))
            y2 = int(y + rad * math.sin(angle))
            self.controller.mouse_move(x2, y2)
            time.sleep(1 / steps * timer)