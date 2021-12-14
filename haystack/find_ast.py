"""AST search-and-replace in the current project

This package will add an option to the Find menu allowing users to search and replace in files in the currently opened project.
"""
import GPS
import gs_utils
from main_view import main_view


@gs_utils.interactive(menu="/Find/Find AST")
def plugin():
    """Creates the Find window when you click the Find AST button in the Find menu."""
    view = main_view()
    view.show_all()
    GPS.MDI.add(view, "Find AST", "Find AST", flags=GPS.MDI.FLAGS_ALWAYS_DESTROY_FLOAT)
    view = GPS.MDI.get("Find AST")
    view.float()


def on_file_changed(hook, file):
    """Reloads the editor when a file is changed on disk."""
    GPS.EditorBuffer.get(file, force=1)
    return 1


GPS.Hook("file_changed_on_disk").add(on_file_changed)
