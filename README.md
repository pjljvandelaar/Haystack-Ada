# Haystack-Ada
Haystack-Ada allows users to perform Abstract Syntax Tree (AST)-based search and replace operations on Ada files within GNAT Studio.
The search patterns must be compilable Ada code, but due to the nature of AST-based searching, formatting of the search pattern does not matter.
This allows one to match code in multiple locations at the same time even if the code fragments themselves are also formatted differently.

To assist in matching a wide variety of code fragments in one go, Haystack supports the use of wildcards.
There are two types of wildcards, those starting with "$S_" and those starting with "$M_".

"$S_" wildcards allow one to match a single thing, be that a single expression, a single statement or anything else.
As long as Ada parses it to a single AST node, the "$S_" wildcard can match it.

"$M_" wildcards allow one to match zero or more things. This makes these types of wildcards more flexible but also more unpredictable.

Wildcards must start with either "$S_" or "$M_" and any alphanumeric string is allowed to follow.

If a wildcard was used to match code in the search pattern, it can be re-used in the replace pattern to copy over what was matched.
Simply write the wildcard identically to how it was written in the search pattern.

## Example
Say you have the following code fragment:
```Ada
if A = B then
 Put_Line ("A equals B");
else
 Put_Line ("A does not equal B");
 A := B;
end if;
```

If you decide you want to flip the if statement, you could write the following search query to match the code fragment:
```Ada
if $S_A = $S_B then
 $M_stmts_true;
else
 $M_stmts_false;
end if;
```

and the following replace statement:
```Ada
if $S_A /= $S_B then
 $M_stmts_false;
else
 $M_stmts_true;
end if;
```

Then the result would look like:
```Ada
if A /= B then
 Put_Line ("A does not equal B");
 A := B;
else
 Put_Line ("A equals B");
end if;
```

## Installation:
### Requirements
There are two requirements:
 - GNAT Studio with Python 3 support (22.0 or newer, 22.0w is still python 2)
 - Python 3.7.6 installed system-wide

You can check what version of python your version of GNAT Studio supports by opening up the python console and typing:
```
>>> import sys
>>> sys.version
```

libadalang is typically included in GNAT Studio binaries from AdaCore.
This can also be checked in GNAT Studio's python console by typing:
```
>>> import libadalang
```

If a ModuleNotFoundError is returned libadalang is not yet installed and you will need to do that yourself by buliding from source:
https://github.com/AdaCore/libadalang/blob/master/user_manual/building.rst

### Install instructions:
There are three methods to launch GNAT Studio with the plug-in installed:

#### 1. GNAT Studio's plug-ins folder
Copy haystack_plugin.py and the Haystack folder to $HOME/.gnatstudio/plug-ins/ on Linux or macOS
or %USERPROFILE%\\.gnatstudio\plug-ins on Windows

#### 2. Environment variable
Add the root folder of Haystack-Ada-Plugin to the GNATSTUDIO_CUSTOM_PATH environment variable.

#### 3. Command line
For an impermanent installation of the plug-in, you can launch GNAT Studio from the command line:
```
$ gnatstudio --load=python:path/to/haystack_plugin.py
```

## Usage:
![Haystack-Plugin](https://user-images.githubusercontent.com/16014794/149525260-b8207da0-419d-4f9a-a2b9-dd56d33cf0cb.PNG)

Once the haystack back-end and plug-in are installed, it can be found in GNAT Studio under the dropdown menu "Find/Find AST"

This is what the Haystack plug-in will look like once it is launched. It is composed of two main textboxes:
 - Find: The search pattern that the user wants to look for within the file
 - Replace: What the user wants to replace the matches with that he previously found

The other things included in the window are as follows:
 - Search query parse rule: Specifies the Ada parse rule that parses the entered search pattern. A user has can either manually enter one or select one from a dropdown menu. If this is not specified or one is chosen that does not parse the search pattern, Haystack will ask the user if it should automatically search for a parse rule that will work to parse the pattern.
 - Case insensitive: This checkbox is unticked by default. If ticked, Haystack will search for pattern matches while ignoring any casing.
 - Where: In this dropdown menu the user is able to select what context Haystack should search for the search pattern.

Finally the buttons:
 - Find: Pressing this button will prompt Haystack to search the selected context for any matches to the search pattern.
 - Find all: Same as Find, only now Haystack will add all found matches to GNAT Studio's Locations view
 - Next: Once matches have been found, this button will select the next match found.
 - Previous: Once matches have been found, this button will select the previous match found.
 - Replace Next: Once matches have been found, this button will apply the replacement to the currently selected match and then select the next match.
 - Replace All: Once matches have been found, this button will apply the replacement to all found matches.

## Related technologies
* [Renaissance-Ada](https://github.com/TNO/Renaissance-Ada) is [ESI](https://esi.nl)'s Renaissance approach to legacy [Ada](https://en.wikipedia.org/wiki/Ada_(programming_language)) software. Haystack-Ada is a partial re-implementation of the rejuvenation library in Python
