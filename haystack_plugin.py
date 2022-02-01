"""AST search-and-replace in the current project

This package will add an option to the Find menu allowing users to
search and replace in files in the currently opened project.
"""
from enum import Enum
from typing import Tuple, List
from gi.repository import Gtk, GLib, Gdk, GObject  # type: ignore # pylint: disable=import-error,unused-import
import libadalang as lal  # type: ignore
import gs_utils  # type: ignore # pylint: disable=import-error
import GPS
from Haystack import api
from Haystack.location import Location
from Haystack import exceptions


@gs_utils.interactive(menu="/Find/Find AST")  # type: ignore
def plugin():
    """Creates the Find window when you click the Find AST button in the Find menu."""
    view = MainView()
    view.show_all()
    GPS.MDI.add(  # pylint: disable=unexpected-keyword-arg
        view,
        "Find AST",
        "Find AST",
        flags=GPS.MDI.FLAGS_ALWAYS_DESTROY_FLOAT,  # pylint: disable=no-member
    )
    view = GPS.MDI.get("Find AST")
    view.float()


def on_file_changed(hook, file):  # pylint: disable=unused-argument
    """Reloads the editor when a file is changed on disk."""
    GPS.EditorBuffer.get(file, force=1)
    return 1


GPS.Hook("file_changed_on_disk").add(on_file_changed)


class SearchContext(Enum):
    """Enum containing all contexts in which you can search for ASTs."""

    CURRENT_FILE = "Current file"
    CURRENT_PROJECT = "Files from current project"


class MainView(Gtk.Grid):
    """The Find window"""

    def __init__(self):
        """Builds the main GUI."""
        super().__init__()
        self.locations: List[Tuple[str, Location]] = []
        self.selected_location: int = -1

        # Create vertical box to contain the dropdown menu and query boxes
        find_replace_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.attach(find_replace_box, 0, 0, 1, 1)

        self.create_grammar_rule_dropdown(find_replace_box)
        self.create_find_text_area(find_replace_box)
        self.create_replace_text_area(find_replace_box)
        self.create_search_location_dropdown(find_replace_box)
        self.create_buttons(find_replace_box)

    def create_grammar_rule_dropdown(self, find_replace_box):
        """
        Creates a textbox where the user can enter the parse rule for the search query.
        Alternatively, the user can click the arrow at the end of the box and select a
        parse rule from a dropdown menu.
        """
        parse_rule_box = Gtk.Box()
        parse_rule_label = Gtk.Label(label="Search query parse rule: ")
        self.find_parse_rule_combo = Gtk.ComboBoxText.new_with_entry()
        for rule in sorted(
            lal.GrammarRule._c_to_py  # pylint: disable=protected-access
        ):
            self.find_parse_rule_combo.append_text(rule)
        self.find_parse_rule_combo.set_wrap_width(4)

        parse_rule_box.pack_start(parse_rule_label, False, False, 0)
        parse_rule_box.pack_start(self.find_parse_rule_combo, False, False, 0)

        find_replace_box.pack_start(parse_rule_box, False, False, 0)

    def create_find_text_area(self, find_replace_box):
        """
        Creates a scrolled window with a textbox inside.
        The user can type the ada code that they would like to search for in here.
        Once the text is big enough to not fit in the textbox anymore, a scrollbar
        is automatically added.
        """
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

    def create_replace_text_area(self, find_replace_box):
        """
        Creates a scrolled window with a textbox inside.
        The user can type the ada code that they would like to use
        as a replacement in here.
        Once the text is big enough to not fit in the textbox anymore,
        a scrollbar is automatically added.
        """
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

    def create_search_location_dropdown(self, find_replace_box):
        """
        Adds a dropdown menu where the user can select what context to search in.
        """
        search_context_box = Gtk.Box()
        search_context_label = Gtk.Label(label="Where ")
        self.search_context_combo = Gtk.ComboBoxText.new_with_entry()
        for context in SearchContext:
            self.search_context_combo.append_text(context.value)
        self.search_context_combo.set_active(0)

        search_context_box.pack_start(search_context_label, False, False, 0)
        search_context_box.pack_start(self.search_context_combo, False, False, 0)

        find_replace_box.pack_start(search_context_box, False, False, 0)

    def create_buttons(self, find_replace_box):
        """
        Creates all the buttons of the GUI, links them to the appropriate
        functions and adds them to the GUI.
        """
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.attach_next_to(button_box, find_replace_box, Gtk.PositionType.RIGHT, 1, 2)

        find_button = Gtk.Button(label="Find")
        find_button.connect("clicked", self.on_find_clicked)

        find_all_button = Gtk.Button(label="Find All")
        find_all_button.connect("clicked", self.on_find_all_clicked)

        next_button = Gtk.Button(label="Next")
        next_button.connect("clicked", self.on_next_clicked)

        previous_button = Gtk.Button(label="Previous")
        previous_button.connect("clicked", self.on_previous_clicked)

        replace_next_button = Gtk.Button(label="Replace next")
        replace_next_button.connect("clicked", self.on_replace_next_clicked)

        replace_button = Gtk.Button(label="Replace All")
        replace_button.connect("clicked", self.on_replace_all_clicked)

        self.contextual_buttons = [
            next_button,
            previous_button,
            replace_next_button,
            replace_button,
        ]
        self.set_button_sensitivity(False)

        self.case_insensitive_button = Gtk.CheckButton(label="Case insensitive")

        button_box.pack_start(self.case_insensitive_button, False, False, 0)
        button_box.pack_end(replace_button, False, False, 0)
        button_box.pack_end(replace_next_button, False, False, 0)
        button_box.pack_end(previous_button, False, False, 0)
        button_box.pack_end(next_button, False, False, 0)
        button_box.pack_end(find_all_button, False, False, 0)
        button_box.pack_end(find_button, False, False, 0)

    def set_button_sensitivity(self, sensitive: bool):
        """
        Changes the sensitivity of the contextual buttons.
        When a button is not sensitive, it is grayed out and cannot be clicked.
        These are the buttons that can only be used when matches have already been found.
        One example is the next button.
        """
        for button in self.contextual_buttons:
            button.set_sensitive(sensitive)

    def on_find_clicked(self, widget):
        """
        Retrieves the entered search query and parse rule,
        then calls the search method appropriate for the selected context.
        """
        self.locations = []
        self.set_button_sensitivity(False)
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

            # Retrieve the right function according to the
            # selected search context and execute that function
            func = switcher.get(selected_context)
            func(editor_buffer, parse_rule, search_query)

            if len(self.locations) > 0:
                self.set_button_sensitivity(True)
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
        If the selected parse rule doesn't work,
        the user is asked whether they want to try other rules.
        """
        editor_buffer = GPS.EditorBuffer.get(file=GPS.File(filepath))
        editor_buffer.save(interactive=True)
        try:
            locations = api.findall_file(
                search_query,
                filepath,
                parse_rule,
                self.case_insensitive_button.get_active(),
            )
        except exceptions.PatternParseException:
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
                    lal.GrammarRule._c_to_py,  # pylint: disable=protected-access
                    self.case_insensitive_button.get_active(),
                )
            else:
                return
        except exceptions.OperandParseException:
            GPS.MDI.dialog(
                "The file could not be parsed. Please check for any errors and fix them."
            )
            return
        for location in locations:
            self.locations.append((filepath, location))

    def on_next_clicked(self, widget):  # pylint: disable=unused-argument
        """When a search query has been executed,
        selects the next matched location found."""
        if len(self.locations) > 0:
            self.selected_location = (self.selected_location + 1) % len(self.locations)
            (filepath, location) = self.locations[self.selected_location]
            select_location(filepath, location)

    def on_previous_clicked(self, widget):  # pylint: disable=unused-argument
        """When a search query has been executed,
        selects the previous matched location found."""
        if len(self.locations) > 0:
            self.selected_location = (self.selected_location - 1) % len(self.locations)
            (filepath, location) = self.locations[self.selected_location]
            select_location(filepath, location)

    def on_replace_next_clicked(self, widget):
        """When a search query has been executed, replaces the currently selected location
        and then selects the next matched location in the current file."""
        # Read replace buffer
        buffer = self.replace_textview.get_buffer()
        text_start, text_end = buffer.get_bounds()
        replacement = buffer.get_text(text_start, text_end, True)

        # Replace currently selected text, save, search again
        api.replace_file(
            self.locations[self.selected_location][0],
            [self.locations[self.selected_location][1]],
            replacement,
        )

        self.selected_location -= 1
        self.on_find_clicked(widget)

    def on_replace_all_clicked(self, widget):  # pylint: disable=unused-argument
        """Replaces all found matches with the text entered into the replace textbox."""
        # Read replace buffer
        buffer = self.replace_textview.get_buffer()
        start, end = buffer.get_bounds()
        replacement = buffer.get_text(start, end, True)

        file_replacements = {}
        for (filepath, replace_location) in self.locations:
            if filepath not in file_replacements:
                file_replacements[filepath] = [replace_location]
            else:
                file_replacements[filepath].append(replace_location)

        for filepath, replace_locations in file_replacements.items():
            api.replace_file(filepath, replace_locations, replacement)

        # Remove found matches
        self.locations = []
        self.selected_location = -1
        self.set_button_sensitivity(False)


def gps_replace(locations: List[Location], replacement: str):
    """
    Replaces the text at a given location in the currently focused
    file with the given replacement using GPS.

    Currently unused, api.replace_file is preferred as it is more tested
    """
    editor_buffer = GPS.EditorBuffer.get()
    for location in locations[::-1]:
        start, end = get_editor_locations(editor_buffer, location)
        end = end.forward_char(-1)
        locations.remove(location)
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


def select_location(filepath: str, location: Location):
    """
    Selects a specified location in a specified file and centers the editor view on it.
    """
    editor_buffer = GPS.EditorBuffer.get(GPS.File(filepath))
    GPS.MDI.get_by_child(editor_buffer.current_view()).raise_window()
    GPS.MDI.get("Find AST").raise_window()
    start, end = get_editor_locations(editor_buffer, location)
    editor_buffer.select(start, end)
    editor_buffer.current_view().center(start)
