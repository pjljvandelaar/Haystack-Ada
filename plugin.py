import GPS
import gs_utils
import re

from gi.repository import Gtk, GLib, Gdk, GObject

@gs_utils.interactive(menu="/Find/Find AST")
def hello_world():
    #GPS.MDI.dialog("Hello World!")

    #a, b = GPS.MDI.input_dialog("Please enter values", "a", "b")
    #print(a, b)

    #button=Gtk.Button('press')
    #button.connect('clicked', on_clicked)
    #GPS.MDI.add(button, "From testgtk", "testgtk")
    #win = GPS.MDI.get('testgtk')
    #win.float()

    win = GridWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    GPS.MDI.add(win, "From testgtk", "testgtk")
    win = GPS.MDI.get("testgtk")
    win.float()

#def on_clicked(*args):
#   GPS.Console().write("button was pressed\n")

class MyWindow(Gtk.Window):
    def __init__(self):
        super(MyWindow, self).__init__(title="Hello World")

        self.box = Gtk.Box(spacing = 6)
        self.add(self.box)

        self.button1 = Gtk.Button(label="Hello")
        self.button1.connect("clicked", self.on_button1_clicked)
        self.box.pack_start(self.button1, True, True, 0)

        self.button2 = Gtk.Button(label="Goodbye")
        self.button2.connect("clicked", self.on_button2_clicked)
        self.box.pack_start(self.button2, True, True, 0)

    def on_button1_clicked(self, widget):
        GPS.Console().write("Hello\n")

    def on_button2_clicked(self, widget):
        GPS.Console().write("Goodbye\n")

class GridWindow(Gtk.Window):
    def __init__(self):
        super(GridWindow, self).__init__(title="Grid Example")
        self.set_default_size(500, 300)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.search_replace_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)
        self.grid.attach(self.search_replace_box, 0, 0, 1, 1)

        self.search_box = Gtk.Box(spacing = 10)
        self.search_label = Gtk.Label(label = "Search")
        self.search_box.pack_start(self.search_label, False, False, 9)

        self.search_window = Gtk.ScrolledWindow()
        self.search_window.set_hexpand(True)
        self.search_window.set_vexpand(True)

        self.search_textview = Gtk.TextView()
        self.search_textview.set_accepts_tab(True)
        self.search_textview.set_editable(True)
        self.search_window.add(self.search_textview)
        self.search_box.pack_start(self.search_window, True, True, 0)

        self.search_replace_box.pack_start(self.search_box, True, True, 0)

        self.replace_box = Gtk.Box(spacing = 10)
        self.replace_label = Gtk.Label(label = "Replace")
        self.replace_box.pack_start(self.replace_label, False, False, 5)

        self.replace_window = Gtk.ScrolledWindow()
        self.replace_window.set_hexpand(True)
        self.replace_window.set_vexpand(True)

        self.replace_textview = Gtk.TextView()
        self.replace_textview.set_accepts_tab(True)
        self.replace_textview.set_editable(True)
        self.replace_window.add(self.replace_textview)
        self.replace_box.pack_start(self.replace_window, True, True, 0)

        self.search_replace_box.pack_start(self.replace_box, True, True, 0)

        self.button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)

        self.button1 = Gtk.Button(label="Search")
        self.button1.connect("clicked", self.on_button1_clicked)
        
        self.button2 = Gtk.Button(label="Replace")
        self.button2.connect("clicked", self.on_button2_clicked)

        self.button_box.pack_end(self.button2, False, False, 0)
        self.button_box.pack_end(self.button1, False, False, 0)

        self.grid.attach_next_to(self.button_box, self.search_replace_box, Gtk.PositionType.RIGHT, 1, 2)

    
    def on_button1_clicked(self, widget):
        buffer = self.search_textview.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)
        text += "\n"
        GPS.Console().write(text)

    def on_button2_clicked(self, widget):
        GPS.Console().write("Replace\n")
