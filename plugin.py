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

        grid = Gtk.Grid()
        self.add(grid)

        search_replace_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)
        grid.attach(search_replace_box, 0, 0, 1, 1)

        search_label = Gtk.Label(label="")
        search_window = Gtk.ScrolledWindow()
        search_window.set_hexpand(True)
        search_window.set_vexpand(True)

        search_textview = Gtk.TextView()
        search_window.add(search_textview)
        search_replace_box.pack_start(search_window, True, True, 0)

        replace_window = Gtk.ScrolledWindow()
        replace_window.set_hexpand(True)
        replace_window.set_vexpand(True)

        replace_textview = Gtk.TextView()
        replace_window.add(replace_textview)
        search_replace_box.pack_start(replace_window, True, True, 0)

        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)

        button1 = Gtk.Button(label="Search")
        button1.connect("clicked", self.on_button1_clicked)
        button_box.pack_start(button1, False, False, 0)
        
        button2 = Gtk.Button(label="Replace")
        button2.connect("clicked", self.on_button2_clicked)
        button_box.pack_start(button2, False, False, 0)
        grid.attach_next_to(button_box, search_replace_box, Gtk.PositionType.RIGHT, 1, 2)
    
    def on_button1_clicked(self, widget):
        #GPS.Console().write("Search\n")

        file = GPS.current_context().file()

        line_list = []
        with open(str(file), "r") as f:
           for line in f:
               line_list.append(line.rstrip("\n"))

        GPS.Console().write(line_list[8])

    def on_button2_clicked(self, widget):
        GPS.Console().write("Replace\n")
