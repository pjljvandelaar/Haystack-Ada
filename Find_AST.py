import GPS
import gs_utils
from searchresult import SearchResult
import libadalang as lal
from replacer import Replacer
from location import Location

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
        self.selected_location = -1
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

        self.find_button = Gtk.Button(label="Find All")
        self.find_button.connect("clicked", self.on_find_clicked)

        self.next_button = Gtk.Button(label="Next")
        self.next_button.connect("clicked", self.on_next_clicked)

        self.replace_next_button = Gtk.Button(label="Replace next")
        self.replace_next_button.connect("clicked", self.on_replace_next_clicked)
        
        self.replace_button = Gtk.Button(label="Replace All")
        self.replace_button.connect("clicked", self.on_replace_clicked)

        self.button_box.pack_end(self.replace_button, False, False, 0)
        self.button_box.pack_end(self.replace_next_button, False, False, 0)
        self.button_box.pack_end(self.next_button, False, False, 0)
        self.button_box.pack_end(self.find_button, False, False, 0)

        self.attach_next_to(self.button_box, self.find_replace_box, Gtk.PositionType.RIGHT, 1, 2)

    
    def on_find_clicked(self, widget):
        # read search buffer
        buffer = self.find_textview.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)

        # get path of currently opened file
        editor_buffer = GPS.EditorBuffer.get()
        self.path = editor_buffer.file().path

        # search for matches in current file
        search = SearchResult(self.path, text, lal.GrammarRule.expr_rule)
        self.locations = search.locations
        console = GPS.Console("Find AST")
        console.write(str(self.locations))

        # select first match
        self.on_next_clicked(widget)

    def on_next_clicked(self, widget):
        editor_buffer = GPS.EditorBuffer.get()
        if len(self.locations) > 0:
            self.selected_location = (self.selected_location + 1) % len(self.locations)
            location = self.locations[self.selected_location]
            start, end = get_editor_locations(editor_buffer, location)
            editor_buffer.select(start, end)
            editor_buffer.current_view().center(start)

    def on_replace_next_clicked(self, widget):
        # Read replace buffer
        buffer = self.replace_textview.get_buffer()
        text_start, text_end = buffer.get_bounds()
        text = buffer.get_text(text_start, text_end, True)

        # Replace currently selected text, search again
        editor_buffer = GPS.EditorBuffer.get()
        start, end = get_editor_locations(editor_buffer, self.locations[self.selected_location])
        end = end.forward_char(-1)
        del self.locations[self.selected_location]
        self.selected_location = self.selected_location - 1
        editor_buffer.delete(start, end)
        editor_buffer.insert(start, text)
        editor_buffer.save(False)
        self.on_find_clicked(widget)


    def on_replace_clicked(self, widget):
        # Read replace buffer
        buffer = self.replace_textview.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)

        # Start replacement
        replacer = Replacer(self.path, self.locations, text)
        replacer.replace()

        # Remove found matches
        self.locations = []
        self.selected_location = -1
    
def get_editor_locations(editor_buffer, location):
    start = editor_buffer.at(location.start_line, location.start_char)
    end = editor_buffer.at(location.end_line, location.end_char)
    return start, end
