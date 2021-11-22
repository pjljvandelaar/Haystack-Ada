# Haystack


## Installation
There are multiple options to launch GNAT studio with the plug-in installed:

### 1. Command line option
You can launch GNAT studio from the command line:
> $ gnatstudio --load=python:path/to/find_ast.py

### 2. Add it to GNAT studio's plug-ins folder
Copy find_ast.py, replacer.py and searchresult.py to $HOME/.gnatstudio/plug-ins/ (%USERPROFILE%\.gnatstudio\plug-ins on Windows).
You can now launch GNAT studio as normal

### 3. Add Haystack folder to GNATSTUDIO_CUSTOM_PATH
Add the root folder of Haystack to the GNATSTUDIO_CUSTOM_PATH environment variable.
You can now launch GNAT studio as normal

## Usage
Once the plug-in has been installed, it can be found in the dropdown menu "Find/Find AST"