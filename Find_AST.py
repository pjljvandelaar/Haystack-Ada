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

        find_replace_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)
        self.attach(find_replace_box, 0, 0, 1, 1)

        self.find_parse_rule_combo = Gtk.ComboBoxText.new_with_entry()
        for rule in sorted(lal.GrammarRule._c_to_py):
            self.find_parse_rule_combo.append_text(rule)
        self.find_parse_rule_combo.set_wrap_width(4)
        
        find_replace_box.pack_start(self.find_parse_rule_combo, False, False, 0)

        find_box = Gtk.Box(spacing = 10)

        find_window = Gtk.ScrolledWindow()
        find_window.set_hexpand(True)
        find_window.set_vexpand(True)
        find_window.set_shadow_type(Gtk.ShadowType.OUT)
        find_window_frame = Gtk.Frame(label="Find")
        find_window_frame.add(find_window)

        self.find_textview = Gtk.TextView()
        self.find_textview.set_accepts_tab(True)
        self.find_textview.set_editable(True)
        find_window.add(self.find_textview)
        find_box.pack_start(find_window_frame, True, True, 0)

        find_replace_box.pack_start(find_box, True, True, 0)

        replace_box = Gtk.Box(spacing = 10)

        replace_window = Gtk.ScrolledWindow()
        replace_window.set_hexpand(True)
        replace_window.set_vexpand(True)
        replace_window.set_shadow_type(Gtk.ShadowType.OUT)
        replace_window_frame = Gtk.Frame(label="Replace")
        replace_window_frame.add(replace_window)

        self.replace_textview = Gtk.TextView()
        self.replace_textview.set_accepts_tab(True)
        self.replace_textview.set_editable(True)
        replace_window.add(self.replace_textview)
        replace_box.pack_start(replace_window_frame, True, True, 0)

        find_replace_box.pack_start(replace_box, True, True, 0)

        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing = 10)

        find_button = Gtk.Button(label="Find All")
        find_button.connect("clicked", self.on_find_clicked)

        next_button = Gtk.Button(label="Next")
        next_button.connect("clicked", self.on_next_clicked)

        replace_next_button = Gtk.Button(label="Replace next")
        replace_next_button.connect("clicked", self.on_replace_next_clicked)
        
        replace_button = Gtk.Button(label="Replace All")
        replace_button.connect("clicked", self.on_replace_clicked)

        # We add the buttons in reverse order, from the end to the front so that they're nicely arranged from the bottom of the window upwards
        button_box.pack_end(replace_button, False, False, 0)
        button_box.pack_end(replace_next_button, False, False, 0)
        button_box.pack_end(next_button, False, False, 0)
        button_box.pack_end(find_button, False, False, 0)

        self.attach_next_to(button_box, find_replace_box, Gtk.PositionType.RIGHT, 1, 2)

    
    def on_find_clicked(self, widget):
        # read search buffer
        buffer = self.find_textview.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)

        # get path of currently opened file
        editor_buffer = GPS.EditorBuffer.get()
        self.path = editor_buffer.file().path

        # Get selected parse rule from combo box or default_grammar_rule if none was entered
        selected_find_rule = self.find_parse_rule_combo.get_active_text()
        if selected_find_rule != '':
            parse_rule = getattr(lal.GrammarRule, selected_find_rule)
        else:
            parse_rule = lal.default_grammar_rule

        # search for matches in current file
        search = SearchResult(self.path, text, parse_rule)
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

        # Replace currently selected text, save, search again
        #replacer = Replacer(self.path, self.locations, text, [self.selected_location])
        #replacer.replace()
        #self.selected_location = -1
        self.gps_replace([self.locations[self.selected_location]], text)
        self.selected_location -= 1
        self.on_find_clicked(widget)


    def on_replace_clicked(self, widget):
        # Read replace buffer
        buffer = self.replace_textview.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)

        # Start replacement
        #replacer = Replacer(self.path, self.locations, text)
        #replacer.replace()
        self.gps_replace(self.locations, text)

        # Remove found matches
        self.locations = []
        self.selected_location = -1

    def gps_replace(self, locations, replacement):
        editor_buffer = GPS.EditorBuffer.get()
        for location in locations[::-1]:
            start, end = get_editor_locations(editor_buffer, location)
            end = end.forward_char(-1)
            self.locations.remove(location)
            editor_buffer.delete(start, end)
            editor_buffer.insert(start, replacement)
        editor_buffer.save(False)
    
def get_editor_locations(editor_buffer, location):
    start = editor_buffer.at(location.start_line, location.start_char)
    end = editor_buffer.at(location.end_line, location.end_char)
    return start, end

       