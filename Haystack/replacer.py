"""
This module is responsible for performing the replace operations.
The two functions called from outside this class are replace_file and replace_string,
depending on what type of input the replacecement is performed.
"""
from typing import List, Tuple
from Haystack.location import Location


def replace_file(
    filepath: str,
    locations: List[Location],
    replacement: str,
    indexes: List[int] = None,
    output: str = None,
):
    """
    Replaces the contents of a file.
    Only sections specified by the list of locations are overwritten
    and replaced by the replacement parameter.

    :param filename: Name of the file that contains the search result.
    :param slocs: List of locations of the search results.
    :param replacement: String that the search match is to be replaced with.
    :param indexes: The indexes of the locations that are to be used for replacement.
    :param output: Name of the file to which the modified code will be outputted.
    """
    lines = _load_file(filepath)
    output_str = _replace(lines, locations, replacement, indexes)
    output = filepath if output is None else output
    _write_file(output, output_str)


def replace_string(
    to_replace: str,
    locations: List[Location],
    replacement: str,
    indexes: List[int] = None,
) -> str:
    """
    Replaces the contents of a string.
    Only sections specified by the list of locations are overwritten
    and replaced by the replacement parameter.

    :param to_replace: The string on which the replacement will be performed.
    :param locations: The list of locations where the replacement needs to be performed.
    :param replacement: The replacement that will be used to replace the matched locations.
    :param indexes: The indexes of the locations that are to be used for replacement.
    """
    lines = to_replace.splitlines()
    output_str = _replace(lines, locations, replacement, indexes)
    return output_str


def _replace(
    lines: List[str],
    locations: List[Location],
    replacement: str,
    indexes: List[int] = None,
) -> str:
    """
    Takes lines, splits them into parts according to the replacement locations,
    generates replacements (whenever wildcards are involved), and stitches the result back together.

    :param lines: The list of individual lines on which the replacement is performed.
    :param locations: The list of locations where the replacement needs to be performed.
    :param replacement: The replacement that will be used to replace the matched locations.
    :param indexes: The indexes of the locations that are to be used for replacement.
    """
    indexes_gen: List[int] = list(range(len(locations))) if indexes is None else indexes
    if not indexes_gen:
        return "\n".join(lines)

    parts, new_replacement = _split_input(lines, locations, replacement, indexes_gen)

    # After splitting the input into parts, we stitch it back together with the
    # replacement in between the unaltered parts.
    output_str = ""
    for idx, part in enumerate(parts):
        for line in part:
            output_str += line
        if idx == len(parts) - 1:
            # If we just added the last part, break the loop
            break
        if new_replacement:
            # If the replacement had a wildcard, add the replacement with whatever the wildard matched.
            output_str += new_replacement[idx]
        else:
            # Else, add the original replacement.
            output_str += replacement
    return output_str


def _split_input(
    lines: List[str], locations: List[Location], replacement: str, indexes: List[int]
) -> Tuple[List[List[str]], List[str]]:
    """
    Splits the lines into parts according to the locations and generates wildcard
    replacements whenever needed.
    The "parts" added to the list are exactly those parts that stay unedited,
    the pieces of the string that need to be replaced are left out.

    :param lines: The list of individual lines on which the replacement is performed.
    :param locations: The list of locations where the replacement needs to be performed.
    :param replacement: The replacement that will be used to replace the matched locations.
    :param indexes: The indexes of the locations that are to be used for replacement.
    """
    parts: List[List[str]] = []
    new_replacement: List[str] = []
    for i, j in enumerate(indexes):
        new_replacement.append(_wildcard_replace(locations, replacement, j))
        start_line = locations[j].start_line
        end_line = locations[j].end_line
        start_char = locations[j].start_char
        end_char = locations[j].end_char
        if i == 0:
            # Add all characters until the first to-be-edited part.
            parts.append(lines[: start_line - 1])
            parts[-1].append(lines[start_line - 1][: start_char - 1])
        else:
            previous_end_line = locations[indexes[i - 1]].end_line
            previous_end_char = locations[indexes[i - 1]].end_char
            if previous_end_line == start_line:
                # If the current replacement happens on the same line as the last replacement,
                # we need to add the unmodified string between the last character of the previous
                # modification until the first character of the current modification.
                parts.append(
                    [
                        lines[previous_end_line - 1][
                            previous_end_char - 1 : start_char - 1
                        ]
                    ]
                )
            else:
                # Else, we simply add the rest of the previous line.
                parts.append([lines[previous_end_line - 1][previous_end_char - 1 :]])
            # Add the lines in between the last to-be-edited line and the current to-be-edited line.
            parts[-1].extend(lines[previous_end_line : start_line - 1])
            if previous_end_line != start_line:
                # If we are not replacing on the same line as the previous replacement,
                # we still need to add the characters of the current line before
                # the specified replacement.
                parts[-1].append(lines[start_line - 1][: start_char - 1])
        if i == len(indexes) - 1:
            # Finally, add all lines and characters after the last edit.
            parts.append([lines[end_line - 1][end_char - 1 :]])
            parts[-1].extend(lines[end_line:])
    return parts, new_replacement


def _wildcard_replace(locations: List[Location], replacement: str, index: int) -> str:
    """
    Performs the replacement in the dictionary of the wildcards
    """
    result = replacement
    for key, value in locations[index].wildcards.items():
        if key in replacement:
            result = result.replace(key, value.text)
    return result


def _load_file(filepath: str) -> List[str]:
    """
    Loads a file's contents into memory as a list of strings
    """
    lines: List[str]
    with open(filepath, "r", encoding="UTF-8") as infile:
        lines = infile.readlines()
    return lines


def _write_file(filepath: str, lines: str):
    """
    Writes the contents of a string to a file, overwriting its original contents
    """
    with open(filepath, "w", encoding="UTF-8") as outfile:
        outfile.write(lines)
