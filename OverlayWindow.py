from Xlib import X, Xutil, display, Xatom
from Xlib.ext import shape

class OverlayWindow:
	def __init__(self, display):
		self.d = display
		self.screen = self.d.screen()

		self.WM_DELETE_WINDOW = self.d.intern_atom('WM_DELETE_WINDOW')
		self.WM_PROTOCOLS = self.d.intern_atom('WM_PROTOCOLS')

		# Create a pixmap to be used for the window background.
		bgpm = self.screen.root.create_pixmap(1, 1, self.screen.root_depth)

		# In my case I chose the color of the rectangle to be red.
		bggc = self.screen.root.create_gc(
			foreground=self.screen.white_pixel,
			background=self.screen.black_pixel
		)

		# we fill the pixel map with red 
		bgpm.fill_rectangle(bggc, 0, 0, 1, 1)
		geometry = self.screen.root.get_geometry()

		# We then create a window with the background pixel map from above (a red window)
		self.window = self.screen.root.create_window(
			0, # x
			0, # y
			geometry.width, # width
			geometry.height, # height
			0, # border_width
			self.screen.root_depth, # depth
			X.InputOutput, # window_class
			X.CopyFromParent, # visual
			background_pixmap=bgpm, # attr
			event_mask=X.StructureNotifyMask, # attr
			colormap=X.CopyFromParent, # attr
			override_redirect=True # attr
		)

		# We want to make sure we're notified of window destruction so we need to enable this protocol
		self.window.set_wm_protocols([self.WM_DELETE_WINDOW])
		self.window.set_wm_hints(flags=Xutil.StateHint, initial_state=Xutil.NormalState)

		atom_net_wm_state = self.d.intern_atom('_NET_WM_STATE')
		atom_net_wm_state_fullscreen = self.d.intern_atom('_NET_WM_STATE_FULLSCREEN')
		atom_net_wm_state_above = self.d.intern_atom('_NET_WM_STATE_ABOVE')
		self.window.change_property(atom_net_wm_state, Xatom.ATOM, 32, [atom_net_wm_state_fullscreen, atom_net_wm_state_above])

		self.window.shape_select_input(0)
		self.window.map()
	
		# Apply changes
		# self.d.flush()
		
	def flush(self):
		self.d.flush()

	def clear_shape(self):
		pm = self.window.create_pixmap(self.window.get_geometry().width, self.window.get_geometry().height, 1)
		pm_gc = pm.create_gc(foreground=1, background=0)
		pm.fill_rectangle(pm_gc, 0, 0, self.window.get_geometry().width, self.window.get_geometry().height)
		pm_gc.free()
		self.window.shape_mask(shape.SO.Subtract, shape.SK.Bounding, 0, 0, pm)

	def point_shape(self, operation, destination_kind, x, y):
		# Create a pixmap to draw the pixel
		pm = self.window.create_pixmap(1, 1, 1)
		pmgc = pm.create_gc(foreground=1, background=0)
		pm.point(pmgc, 0, 0)
		pmgc.free()

		# Apply the pixel to the window
		self.window.shape_mask(operation, destination_kind, x, y, pm)

	def point_draw(self, x, y, color):
		wgc = self.window.create_gc(foreground=color, background=self.screen.black_pixel)
		self.window.point(wgc, x, y)
		wgc.free()

	def poly_point_shape(self, operation, destination_kind, points):
		if not points:
			return
		xs = [p[0] for p in points]
		ys = [p[1] for p in points]
		x0 = min(xs)
		y0 = min(ys)
		w = max(xs) - x0 + 1
		h = max(ys) - y0 + 1
		adjusted = [(x - x0, y - y0) for (x, y) in points]
		pm = self.window.create_pixmap(w, h, 1)
		pm_gc = pm.create_gc(foreground=1, background=0)
		pm.poly_point(pm_gc, X.CoordModeOrigin, adjusted)
		pm_gc.free()
		self.window.shape_mask(operation, destination_kind, x0, y0, pm)

	def poly_point_draw(self, points, color):
		if not points:
			return
		# xs = [p[0] for p in points]
		# ys = [p[1] for p in points]
		# x0 = min(xs)
		# y0 = min(ys)
		# w = max(xs) - x0 + 1
		# h = max(ys) - y0 + 1
		# adjusted = [(x - x0, y - y0) for (x, y) in points]
		gc = self.window.create_gc(foreground=color, background=self.screen.black_pixel)
		self.window.poly_point(gc, X.CoordModeOrigin, points)
		gc.free()

	def line_shape(self, operation, destination_kind, x1, y1, x2, y2):
		# Compute bounding box for the line
		x0 = min(x1, x2)
		y0 = min(y1, y2)
		w = abs(x2 - x1) + 1
		h = abs(y2 - y1) + 1
		# Create a 1-bit pixmap of the size of the bounding box
		pm = self.window.create_pixmap(w, h, 1)
		pm_gc = pm.create_gc(foreground=1, background=0)
		# Draw the line with coordinates relative to the pixmap
		pm.line(pm_gc, x1 - x0, y1 - y0, x2 - x0, y2 - y0)
		pm_gc.free()
		self.window.shape_mask(operation, destination_kind, x0, y0, pm)

	def line_draw(self, x1, y1, x2, y2, color):
		gc = self.window.create_gc(foreground=color, background=self.screen.black_pixel)
		self.window.line(gc, x1, y1, x2, y2)
		gc.free()

	# Rectangle wrappers
	def rectangle_shape(self, operation, destination_kind, x, y, width, height):
		pm = self.window.create_pixmap(width + 1, height + 1, 1)
		pm_gc = pm.create_gc(foreground=1, background=0)
		# Draw the outline rectangle in the pixmap
		pm.rectangle(pm_gc, 0, 0, width, height)
		pm_gc.free()
		self.window.shape_mask(operation, destination_kind, x, y, pm)

	def rectangle_draw(self, x, y, width, height, color):
		gc = self.window.create_gc(foreground=color, background=self.screen.black_pixel)
		self.window.rectangle(gc, x, y, width, height)
		gc.free()

	# Filled rectangle wrappers
	def fill_rectangle_shape(self, operation, destination_kind, x, y, width, height):
		pm = self.window.create_pixmap(width, height, 1)
		pm_gc = pm.create_gc(foreground=1, background=0)
		pm.fill_rectangle(pm_gc, 0, 0, width, height)
		pm_gc.free()
		self.window.shape_mask(operation, destination_kind, x, y, pm)

	def fill_rectangle_draw(self, x, y, width, height, color):
		gc = self.window.create_gc(foreground=color, background=self.screen.black_pixel)
		self.window.fill_rectangle(gc, x, y, width, height)
		gc.free()

	# Arc wrappers
	def arc_shape(self, operation, destination_kind, x, y, width, height, angle1, angle2):
		pm = self.window.create_pixmap(width + 1, height + 1, 1)
		pm_gc = pm.create_gc(foreground=1, background=0)
		pm.arc(pm_gc, 0, 0, width, height, int(angle1 * 64), int(angle2 * 64))
		pm_gc.free()
		self.window.shape_mask(operation, destination_kind, x, y, pm)

	def arc_draw(self, x, y, width, height, angle1, angle2, color):
		gc = self.window.create_gc(foreground=color, background=self.screen.black_pixel)
		self.window.arc(gc, x, y, width, height, int(angle1 * 64), int(angle2 * 64))
		gc.free()

	# Filled arc wrappers
	def fill_arc_shape(self, operation, destination_kind, x, y, width, height, angle1, angle2):
		pm = self.window.create_pixmap(width + 1, height + 1, 1)
		pm_gc = pm.create_gc(foreground=1, background=0)
		pm.fill_arc(pm_gc, 0, 0, width, height, int(angle1 * 64), int(angle2 * 64))
		pm_gc.free()
		self.window.shape_mask(operation, destination_kind, x, y, pm)

	def fill_arc_draw(self, x, y, width, height, angle1, angle2, color):
		gc = self.window.create_gc(foreground=color, background=self.screen.black_pixel)
		self.window.fill_arc(gc, x, y, width, height, int(angle1 * 64), int(angle2 * 64))
		gc.free()

	# Poly-line wrappers
	def poly_line_shape(self, operation, destination_kind, points):
		if not points:
			return
		xs = [p[0] for p in points]
		ys = [p[1] for p in points]
		x0 = min(xs)
		y0 = min(ys)
		w = max(xs) - x0 + 1
		h = max(ys) - y0 + 1
		# Adjust points relative to the pixmap
		adjusted = [(x - x0, y - y0) for (x, y) in points]
		pm = self.window.create_pixmap(w, h, 1)
		pm_gc = pm.create_gc(foreground=1, background=0)
		pm.poly_line(pm_gc, X.CoordModeOrigin, adjusted)
		pm_gc.free()
		self.window.shape_mask(operation, destination_kind, x0, y0, pm)

	def poly_line_draw(self, points, color):
		gc = self.window.create_gc(foreground=color, background=self.screen.black_pixel)
		self.window.poly_line(gc, X.CoordModeOrigin, points)
		gc.free()

	def fill_poly_shape(self, operation, destination_kind, points):
		if not points:
			return
		xs = [p[0] for p in points]
		ys = [p[1] for p in points]
		x0 = min(xs)
		y0 = min(ys)
		w = max(xs) - x0 + 1
		h = max(ys) - y0 + 1
		adjusted = [(x - x0, y - y0) for (x, y) in points]
		pm = self.window.create_pixmap(w, h, 1)
		pm_gc = pm.create_gc(foreground=1, background=0)
		pm.fill_poly(pm_gc, X.CoordModeOrigin, X.Complex, adjusted)
		pm_gc.free()
		self.window.shape_mask(operation, destination_kind, x0, y0, pm)

	def fill_poly_draw(self, points, color):
		gc = self.window.create_gc(foreground=color, background=self.screen.black_pixel)
		self.window.fill_poly(gc, X.CoordModeOrigin, X.Complex, points)
		gc.free()