import GPS
import gs_utils
import searchresult as sr
import libadalang as lal
import replacer as r

from gi.repository import Gtk, GLib, Gdk, GObject

@gs_utils.interactive(menu="/Find/Find AST")
def plugin():
    win = Grid()
    win.show_all()
    GPS.MDI.add(win, "FindAST", "FindAST",
                flags=GPS.MDI.FLAGS_ALWAYS_DESTROY_FLOAT)
    win = GPS.MDI.get("FindAST")
    win.float()

def on_file_changed(hook, file):
    ed = GPS.EditorBuffer.get(file, force = 1)
    return 1

GPS.Hook("file_changed_on_disk").add(on_file_changed)

class Grid(Gtk.Grid):
    def __init__(self):
        super(Grid, self).__init__()
        self.locations = []
        self.path = None

        self.find_replace_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)
        self.attach(self.find_replace_box, 0, 0, 1, 1)

        self.find_box = Gtk.Box(spacing = 10)
        self.find_box_frame = Gtk.Frame()
        self.find_box_frame.add(self.find_box)

        self.find_window = Gtk.ScrolledWindow()
        self.find_window.set_hexpand(True)
        self.find_window.set_vexpand(True)
        self.find_window.set_shadow_type(Gtk.ShadowType.IN)
        self.find_window_frame = Gtk.Frame(label="Find")
        self.find_window_frame.add(self.find_window)
        self.find_window_frame.set_shadow_type(Gtk.ShadowType.IN)

        self.find_textview = Gtk.TextView()
        self.find_textview.set_accepts_tab(True)
        self.find_textview.set_editable(True)
        self.find_window.add(self.find_textview)
        self.find_box.pack_start(self.find_window_frame, True, True, 0)

        self.find_replace_box.pack_start(self.find_box_frame, True, True, 0)

        self.replace_box = Gtk.Box(spacing = 10)
        self.replace_box_frame = Gtk.Frame()
        self.replace_box_frame.add(self.replace_box)

        self.replace_window = Gtk.ScrolledWindow()
        self.replace_window.set_hexpand(True)
        self.replace_window.set_vexpand(True)
        self.replace_window.set_shadow_type(Gtk.ShadowType.IN)
        self.replace_window_frame = Gtk.Frame(label="Replace")
        self.replace_window_frame.add(self.replace_window)
        self.replace_window_frame.set_shadow_type(Gtk.ShadowType.IN)

        self.replace_textview = Gtk.TextView()
        self.replace_textview.set_accepts_tab(True)
        self.replace_textview.set_editable(True)
        self.replace_window.add(self.replace_textview)
        self.replace_box.pack_start(self.replace_window_frame, True, True, 0)

        self.find_replace_box.pack_start(self.replace_box_frame, True, True, 0)

        self.button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)

        self.findButton = Gtk.Button(label="Find All")
        self.findButton.connect("clicked", self.on_find_clicked)
        
        self.replaceButton = Gtk.Button(label="Replace All")
        self.replaceButton.connect("clicked", self.on_replace_clicked)

        self.button_box.pack_end(self.replaceButton, False, False, 0)
        self.button_box.pack_end(self.findButton, False, False, 0)

        self.attach_next_to(self.button_box, self.find_replace_box, Gtk.PositionType.RIGHT, 1, 2)

    
    def on_find_clicked(self, widget):
        buffer = self.find_textview.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)
        self.path = GPS.EditorBuffer.get().file().path
        search = sr.SearchResult(self.path, text, lal.GrammarRule.expr_rule)
        console = GPS.Console("Find AST")
        console.write(str(search.locations))
        self.locations = search.locations



    def on_replace_clicked(self, widget):
        buffer = self.replace_textview.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)
        replacer = r.Replacer(self.path, self.locations, text)
        replacer.replace()
