#!/usr/bin/python

from Xlib import X, Xutil, display, Xatom
from Xlib.ext import shape

class OutlineWindow:
	def __init__(self, display, x, y, w, h, lw=3):
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

		# # Create an outer rectangle that will be the outer edge of the visible rectangle
		outer_rect = self.window.create_pixmap(w, h, 1)
		gc = outer_rect.create_gc(foreground=1, background=0)
		# coordinates within the graphical context are always relative to itself - not the screen!
		outer_rect.fill_rectangle(gc, 50, 50, w, h)
		gc.free()

		# Create an inner rectangle that is slightly smaller to represent the inner edge of the rectangle
		inner_rect = self.window.create_pixmap(w - (lw * 2), h - (lw * 2), 1)
		gc = inner_rect.create_gc(foreground=1, background=0)
		inner_rect.fill_rectangle(gc, 50, 50, w - (lw * 2), h - (lw * 2))
		gc.free()

		# First add the outer rectangle within the window at x y coordinates
		self.window.shape_mask(shape.SO.Set, shape.SK.Bounding, x, y, outer_rect)

		# Now subtract the inner rectangle at the same coordinates + line width from the outer rect
		# This creates a red rectangular outline that can be clicked through
		self.window.shape_mask(shape.SO.Subtract, shape.SK.Bounding, x + lw, y + lw, inner_rect)
		self.window.shape_select_input(0)
		self.window.map()

		atom_net_wm_state = self.d.intern_atom('_NET_WM_STATE')
		atom_net_wm_state_fullscreen = self.d.intern_atom('_NET_WM_STATE_FULLSCREEN')
		atom_net_wm_state_above = self.d.intern_atom('_NET_WM_STATE_ABOVE')
		self.window.change_property(atom_net_wm_state, Xatom.ATOM, 32, [atom_net_wm_state_fullscreen, atom_net_wm_state_above])

		# # # Définir la transparence de la fenêtre
		# opacity = int(0.5 * 0xFFFFFFFF)  # 0.5 pour 50% de transparence
		# atom_net_wm_window_opacity = display.intern_atom('_NET_WM_WINDOW_OPACITY')
		# self.window.change_property(atom_net_wm_window_opacity, Xatom.CARDINAL, 32, [opacity])

		tmpgc = self.window.create_gc(foreground=self.screen.black_pixel, background=self.screen.white_pixel)
		self.window.fill_rectangle(tmpgc, 50, 50, 10, 10)
		tmpgc.free()

		# Apply changes
		self.d.flush()

	# Main loop, handling events
	def loop(self):
		while True:
			e = self.d.next_event()

			# Window has been destroyed, quit
			if e.type == X.DestroyNotify:
				break

			# Somebody wants to tell us something
			elif e.type == X.ClientMessage:
				if e.client_type == self.WM_PROTOCOLS:
					fmt, data = e.data
					if fmt == 32 and data[0] == self.WM_DELETE_WINDOW:
						break

if __name__ == '__main__':
	OutlineWindow(display.Display(), 0, 0, 200, 200).loop()