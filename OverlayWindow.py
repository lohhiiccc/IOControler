#!/usr/bin/python

from Xlib import X, Xutil, display, Xatom
from Xlib.ext import shape

class OverlayWindow:
	def __init__(self, display):
		self.d = display

		self.screen = self.d.screen()

		self.WM_DELETE_WINDOW = self.d.intern_atom('WM_DELETE_WINDOW')
		self.WM_PROTOCOLS = self.d.intern_atom('WM_PROTOCOLS')

		# Creates a pixel map that will be used to draw the areas that aren't masked
		bgpm = self.screen.root.create_pixmap(1, 1, self.screen.root_depth)

		# In my case I chose the color of the rectangle to be red.
		bggc = self.screen.root.create_gc(
			foreground=0xff0000,
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

# if __name__ == '__main__':
# 	OutlineWindow(display.Display(), 0, 0, 200, 200)