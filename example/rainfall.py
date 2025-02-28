from Xlib import display
from Xlib.ext import shape

from IOController import Controller
from OverlayWindow import OverlayWindow
from MouseMovementUtils import MouseMovementUtils

import time
import math

dsp = display.Display()
ctr = Controller(dsp)
overlay = OverlayWindow(dsp)
mouse = MouseMovementUtils(ctr)

width, height = ctr.get_screen_resolution()
CenterX : int = int(width * .5)
CenterY : int = int(height * .5)
overlay.point_shape(shape.SO.Set, shape.SK.Bounding, 0, 0)
overlay.point_draw(0, 0, 0x0)



def rotate_point(p, angle):
	x, y = p
	x1 = x * math.cos(angle) - y * math.sin(angle)
	y1 = x * math.sin(angle) + y * math.cos(angle)
	return (x1, y1)

def rotate_points(points, angle):
	return [rotate_point(p, angle) for p in points]

def draw_drop(o: OverlayWindow, x: int, y: int, scale: float, roation: float, quality: int, color):
	drop_points = []
	for i in range(0, quality):
		step = float(i) / float(quality) * 2 * math.pi - math.pi
		px = 1 * (1 - math.sin(step)) * math.cos(step)
		py = 5 / 2 * (math.sin(step) - 1)
		drop_points.append((int(px * scale), int(-py * scale)))
	drop_points.append(drop_points[0])
	rotated_points = rotate_points(drop_points, roation)
	offset_points = [(int(p[0] + x), int(p[1] + y)) for p in rotated_points]
	o.fill_poly_shape(shape.SO.Union, shape.SK.Bounding, offset_points)
	o.fill_poly_draw(offset_points, color)



# draw_drop(overlay, CenterX, CenterY, 100, 3.14, 100, 0x55aaff)

angle_radians = 0
for i in range(0, 360):
	overlay.clear_shape()
	draw_drop(overlay, CenterX, CenterY, 100, angle_radians, 100, 0x55aaff)
	overlay.flush()
	angle_radians = i / 180 * math.pi
	#time.sleep(0.01)


overlay.flush()

# ctr.set_gamma(0.5, 1, 1)

# time.sleep(2)