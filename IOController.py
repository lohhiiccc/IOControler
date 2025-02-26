from Xlib import display, X, XK
from enum import Enum
import time

class Action(Enum):
    STROK = 1
    PRESS = 2
    RELEASE = 3
    SHORTCUT = 4

class Controller:
    def __init__(self):
        self.d = display.Display()
        self.actions = {
            Action.STROK: self.key_stroke,
            Action.PRESS: self.key_press,
            Action.RELEASE: self.key_release,
            Action.SHORTCUT: self.shortcut
        }
    
    def execute(self, action, keys):
        self.actions[action](keys)

    def key_stroke(self, key_name):
        keysym = XK.string_to_keysym(key_name)
        keycode = self.d.keysym_to_keycode(keysym)
        self.d.xtest_fake_input(X.KeyPress, keycode)
        self.d.xtest_fake_input(X.KeyRelease, keycode)
        self.d.sync()

    def key_press(self, key_name):
        keysym = XK.string_to_keysym(key_name)
        keycode = self.d.keysym_to_keycode(keysym)
        self.d.xtest_fake_input(X.KeyPress, keycode)
        self.d.sync()
    
    def key_release(self, key_name):
        keysym = XK.string_to_keysym(key_name)
        keycode = self.d.keysym_to_keycode(keysym)
        self.d.xtest_fake_input(X.KeyRelease, keycode)
        self.d.sync()

    def shortcut(self, keys):
        """
        Simulates a keyboard shortcut by pressing all keys in order and then releasing them in reverse order.
        
        :param keys: List of key names as strings, e.g., ["Control_L", "C"]
        """
        keycodes = []
        
        # Convert each key name to its corresponding keycode.
        for key in keys:
            keysym = XK.string_to_keysym(key)
            # print(keysym)
            keycode = self.d.keysym_to_keycode(keysym)
            if (keycode == 0):
                # print(f"Key not found: {key}")
                raise Exception("Key not found {key}")
            keycodes.append(keycode)
        
        # Press all keys in the order provided.
        for keycode in keycodes:
            self.d.xtest_fake_input(X.KeyPress, keycode)
        self.d.sync()
        
        # Optional small delay to simulate a realistic key hold.
        # time.sleep(0.05)
        
        # Release keys in reverse order.
        for keycode in reversed(keycodes):
            self.d.xtest_fake_input(X.KeyRelease, keycode)
        self.d.sync()




# tests

# def key_stroke(key_name):
#     d = display.Display()
#     keysym = XK.string_to_keysym(key_name)
#     keycode = d.keysym_to_keycode(keysym)
#     d.xtest_fake_input(X.KeyPress, keycode)
#     d.xtest_fake_input(X.KeyRelease, keycode)
#     d.sync()

# def key_press(key_name):
#     d = display.Display()
#     keysym = XK.string_to_keysym(key_name)
#     keycode = d.keysym_to_keycode(keysym)
#     d.xtest_fake_input(X.KeyPress, keycode)
#     d.sync()

# def key_release(key_name):
#     d = display.Display()
#     keysym = XK.string_to_keysym(key_name)
#     keycode = d.keysym_to_keycode(keysym)
#     d.xtest_fake_input(X.KeyRelease, keycode)
#     d.sync()

# def shortcut(keys):
#     """
#     Simulates a keyboard shortcut by pressing all keys in order and then releasing them in reverse order.
    
#     :param keys: List of key names as strings, e.g., ["Control_L", "C"]
#     """
#     d = display.Display()
#     keycodes = []
    
#     # Convert each key name to its corresponding keycode.
#     for key in keys:
#         keysym = XK.string_to_keysym(key)
#         # print(keysym)
#         keycode = d.keysym_to_keycode(keysym)
#         keycodes.append(keycode)
    
#     # Press all keys in the order provided.
#     for keycode in keycodes:
#         d.xtest_fake_input(X.KeyPress, keycode)
#     d.sync()
    
#     # Optional small delay to simulate a realistic key hold.
#     # time.sleep(0.05)
    
#     # Release keys in reverse order.
#     for keycode in reversed(keycodes):
#         d.xtest_fake_input(X.KeyRelease, keycode)
#     d.sync()

# def mouse_move(x, y):
#     """
#     Moves the mouse pointer to the specified (x, y) screen coordinates.
#     """
#     d = display.Display()
#     # Simulate mouse movement. The second argument is not used for motion events.
#     d.xtest_fake_input(X.MotionNotify, 0, x, y)
#     d.sync()

# def mouse_click(button=1):
#     """
#     Simulates a mouse click for the specified button.
#     Default button is 1 (left click); 2 for middle, 3 for right.
#     """
#     d = display.Display()
#     # Simulate /home/kchillon/Documents/scripts/useful/IOController.py0.05)  # Short delay to mimic a real click
#     # Simulate button release
#     d.xtest_fake_input(X.ButtonRelease, button)
#     d.sync()

# # Example usage:
# move_mouse(100, 200)  # Moves the pointer to position (100, 200)
# mouse_click(1)        # Simulates a left mouse click
