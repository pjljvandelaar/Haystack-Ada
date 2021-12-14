from enum import Enum
import libadalang as lal  # type: ignore
import GPS
import api
from location import Location
from typing import Tuple, List

from gi.repository import Gtk, GLib, Gdk, GObject  # type: ignore


class SearchContext(Enum):
    """Enum containing all contexts in which you can search for ASTs."""

    CURRENT_FILE = "Current file"
    CURRENT_PROJECT = "Files from current project"


class main_view(Gtk.Grid):
    """The Find window"""

    def __init__(self):
        """Builds the main GUI."""
        super().__init__()
        self.locations: List[Tuple[str, Location]] = []
        self.selected_location: int = -1

        # Create vertical box to contain the dropdown menu and query boxes
        find_replace_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.attach(find_replace_box, 0, 0, 1, 1)

        # create grammar rule dropdown menu
        parse_rule_box = Gtk.Box()
        parse_rule_label = Gtk.Label(label="Search query parse rule: ")
        self.find_parse_rule_combo = Gtk.ComboBoxText.new_with_entry()
        for rule in sorted(lal.GrammarRule._c_to_py):
            self.find_parse_rule_combo.append_text(rule)
        self.find_parse_rule_combo.set_wrap_width(4)

        parse_rule_box.pack_start(parse_rule_label, False, False, 0)
        parse_rule_box.pack_start(self.find_parse_rule_combo, False, False, 0)

        find_replace_box.pack_start(parse_rule_box, False, False, 0)

        # Create text area for the search query and add it to the window
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
        find_replace_box.pack_start(find_window_frame, True, True, 0)

        # Create text area for the replace query and add it to the window
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
        find_replace_box.pack_start(replace_window_frame, True, True, 0)

        # Create search location dropdown menu
        search_context_box = Gtk.Box()
        search_context_label = Gtk.Label(label="Where ")
        self.search_context_combo = Gtk.ComboBoxText.new_with_entry()
        for context in SearchContext:
            self.search_context_combo.append_text(context.value)
        self.search_context_combo.set_active(0)

        search_context_box.pack_start(search_context_label, False, False, 0)
        search_context_box.pack_start(self.search_context_combo, False, False, 0)

        find_replace_box.pack_start(search_context_box, False, False, 0)

        # Create vertical box containing all buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.attach_next_to(button_box, find_replace_box, Gtk.PositionType.RIGHT, 1, 2)

        # Create all buttons and add them to the button box
        find_button = Gtk.Button(label="Find")
        find_button.connect("clicked", self.on_find_clicked)

        next_button = Gtk.Button(label="Next")
        next_button.connect("clicked", self.on_next_clicked)

        find_all_button = Gtk.Button(label="Find All")
        find_all_button.connect("clicked", self.on_find_all_clicked)

        replace_next_button = Gtk.Button(label="Replace next")
        replace_next_button.connect("clicked", self.on_replace_next_clicked)

        replace_button = Gtk.Button(label="Replace All")
        replace_button.connect("clicked", self.on_replace_all_clicked)

        self.case_insensitive_button = Gtk.CheckButton(label="Case insensitive")

        button_box.pack_start(self.case_insensitive_button, False, False, 0)
        button_box.pack_end(replace_button, False, False, 0)
        button_box.pack_end(replace_next_button, False, False, 0)
        button_box.pack_end(find_all_button, False, False, 0)
        button_box.pack_end(next_button, False, False, 0)
        button_box.pack_end(find_button, False, False, 0)

    def on_find_clicked(self, widget):
        """
        Retrieves the entered search query and parse rule, then calls the search method appropriate for the selected context.
        """
        # Read search buffer
        buffer = self.find_textview.get_buffer()
        start, end = buffer.get_bounds()
        search_query = buffer.get_text(start, end, True)

        # Get buffer of currently opened file
        editor_buffer = GPS.EditorBuffer.get()

        if editor_buffer is not None:
            # Get selected parse rule from combo box or default_grammar_rule if none was entered
            selected_find_rule = self.find_parse_rule_combo.get_active_text()
            if selected_find_rule != "":
                parse_rule = getattr(lal.GrammarRule, selected_find_rule)
            else:
                parse_rule = lal.default_grammar_rule

            selected_context = self.search_context_combo.get_active_text()

            # Link available contexts to the appropriate search function
            switcher = {
                SearchContext.CURRENT_FILE.value: self.search_current_file,
                SearchContext.CURRENT_PROJECT.value: self.search_current_project,
            }

            # Retrieve the right function according to the selected search context and execute that function
            func = switcher.get(selected_context)
            func(editor_buffer, parse_rule, search_query)

            # select first match
            self.on_next_clicked(widget)

    def on_find_all_clicked(self, widget):
        """
        Executes a search operation and adds the found locations to GNAT Studio's locations view
        """
        self.on_find_clicked(widget)
        locations_to_gnat(self.locations)

    def search_current_file(
        self,
        editor_buffer: GPS.EditorBuffer,
        parse_rule: lal.GrammarRule,
        search_query: str,
    ):
        """Searches the currently opened file for the provided search query."""
        filepath = editor_buffer.file().path
        # search for matches in current file
        self.execute_search(filepath, search_query, parse_rule)

    def search_current_project(
        self,
        editor_buffer: GPS.EditorBuffer,
        parse_rule: lal.GrammarRule,
        search_query: str,
    ):
        """Searches the entire project for the provided search query."""
        current_project = editor_buffer.file().project()

        source_dirs: List[str] = current_project.source_dirs()
        for directory in source_dirs:
            directory = directory + "*.adb"
            filepaths: str = GPS.dir(directory)
            for filepath in filepaths:
                self.execute_search(filepath, search_query, parse_rule)

    def execute_search(
        self, filepath: str, search_query: str, parse_rule: lal.GrammarRule
    ):
        """
        Searches in the specified file for the specified search query.
        If the selected parse rule doesn't work, the user is asked whether they want to try other rules.
        """
        try:
            locations = api.findall_file(
                search_query,
                filepath,
                parse_rule,
                self.case_insensitive_button.get_active(),
            )
        except ValueError:
            choice = GPS.MDI.combo_selection_dialog(
                "Try other rules?",
                "Rule "
                + str(parse_rule)
                + " did not parse your search query, should we try other parse rules?",
                ["Yes", "No"],
            )
            if choice == "Yes":
                locations = api.findall_file_try_rules(
                    search_query,
                    filepath,
                    lal.GrammarRule._c_to_py,
                    self.case_insensitive_button.get_active(),
                )
            else:
                return
        for location in locations:
            self.locations.append((filepath, location))

    def on_next_clicked(self, widget):
        """When a search query has been executed, selects the next matched location
        found in the current file."""
        if len(self.locations) > 0:
            self.selected_location = (self.selected_location + 1) % len(self.locations)
            (filepath, location) = self.locations[self.selected_location]
            editor_buffer = GPS.EditorBuffer.get(GPS.File(filepath))
            GPS.MDI.get_by_child(editor_buffer.current_view()).raise_window()
            GPS.MDI.get("FindAST").raise_window()
            start, end = get_editor_locations(editor_buffer, location)
            editor_buffer.select(start, end)
            editor_buffer.current_view().center(start)

    def on_replace_next_clicked(self, widget):
        """When a search query has been executed, replaces the currently selected location
        and then selects the next matched location in the current file."""
        # Read replace buffer
        buffer = self.replace_textview.get_buffer()
        text_start, text_end = buffer.get_bounds()
        text = buffer.get_text(text_start, text_end, True)

        # Replace currently selected text, save, search again
        self.gps_replace([self.locations[self.selected_location]], text)
        self.selected_location -= 1
        self.on_find_clicked(widget)

    def on_replace_all_clicked(self, widget):
        """Replaces all found matches with the text entered into the replace textbox."""
        # Read replace buffer
        buffer = self.replace_textview.get_buffer()
        start, end = buffer.get_bounds()
        replacement = buffer.get_text(start, end, True)

        editor_buffer = GPS.EditorBuffer.get()
        current_file = editor_buffer.file().path

        console = GPS.Console("Find AST")

        file_replacements = {}
        for (filepath, replace_location) in self.locations:
            if filepath not in file_replacements:
                file_replacements[filepath] = [replace_location]
            else:
                file_replacements[filepath].append(replace_location)

        for filepath, replace_locations in file_replacements.items():
            if filepath == current_file:
                string = "Current file: " + filepath + "\n"
                console.write(string)
                # gps_replace(replace_locations, replacement)
                api.replace_file(filepath, replace_locations, replacement)
            elif len(replace_locations) > 0:
                string = "Other file: " + filepath + "\n"
                console.write(string)
                api.replace_file(filepath, replace_locations, replacement)

        # Remove found matches
        self.locations = []
        self.selected_location = -1


def gps_replace(locations: List[Location], replacement: str):
    """
    Replaces the text at a given location in the currently focused file with the given replacement using GPS.

    Currently unused, api.replace_file is preferred as it is more tested
    """
    editor_buffer = GPS.EditorBuffer.get()
    console = GPS.Console("Find AST")
    console.write("Called gps_replace")
    for location in locations[::-1]:
        start, end = get_editor_locations(editor_buffer, location)
        end = end.forward_char(-1)
        locations.remove(location)
        console.write(str(location) + " ")
        editor_buffer.delete(start, end)
        editor_buffer.insert(start, replacement)
    editor_buffer.save(False)


def get_editor_locations(
    editor_buffer: GPS.EditorBuffer, location: Location
) -> Tuple[GPS.EditorLocation, GPS.EditorLocation]:
    """Converts a Location to two GPS.EditorLocations"""
    start = editor_buffer.at(location.start_line, location.start_char)
    end = editor_buffer.at(location.end_line, location.end_char)
    return start, end


def locations_to_gnat(locations: List[Tuple[str, Location]]):
    """Adds a list of locations to GNAT's locations view"""
    GPS.Locations.remove_category("Find AST")
    for (filepath, location) in locations:
        file = GPS.File(filepath)
        editor_buffer = GPS.EditorBuffer.get(file)
        start, end = get_editor_locations(editor_buffer, location)
        chars = editor_buffer.get_chars(
            start.beginning_of_line(), end.end_of_line().forward_char(-1)
        )
        GPS.Locations.add("Find AST", file, start.line(), start.column(), chars)
