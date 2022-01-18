"""
This module is responsible for performing the replace operations.
The two functions called from outside this class are replace_file and replace_string,
depending on what type of input the replacecement is performed.
"""
from typing import List
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

    :param filename: Name of the file that contains the search result
    :type filename: str
    :param slocs: List of locations of the search results
    :type slocs: list
    :param replacement: String that the search match is to be replaced with
    :type replacement: str
    :param indexes: Indexes corresponding to the slocs list elements that are to be replaced
    :type indexes: list, optional
    :param output: Name of the file to which the modified code will be outputted
    :type output: str, optional
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
    indexes_gen: List[int] = (
        [i for i in range(len(locations))] if indexes is None else indexes
    )
    parts: List[List[str]] = []
    new_replacement: List[str] = []
    for i, j in enumerate(indexes_gen):
        new_replacement.append(_wildcard_replace(locations, replacement, j))
        start_line = locations[j].start_line
        end_line = locations[j].end_line
        start_char = locations[j].start_char
        end_char = locations[j].end_char
        if i == 0:
            parts.append(lines[: start_line - 1])
            parts[-1].append(lines[start_line - 1][: start_char - 1])
        else:
            previous_end_line = locations[indexes_gen[i - 1]].end_line
            previous_end_char = locations[indexes_gen[i - 1]].end_char
            if previous_end_line == start_line:
                parts.append(
                    [
                        lines[previous_end_line - 1][
                            previous_end_char - 1 : start_char - 1
                        ]
                    ]
                )
            else:
                parts.append([lines[previous_end_line - 1][previous_end_char - 1 :]])
            parts[-1].extend(lines[previous_end_line : start_line - 1])
            if previous_end_line != start_line:
                parts[-1].append(lines[start_line - 1][: start_char - 1])
        if i == len(indexes_gen) - 1:
            parts.append([lines[end_line - 1][end_char - 1 :]])
            parts[-1].extend(lines[end_line:])

    output_str = "" if indexes_gen else "\n".join(lines)
    for idx, part in enumerate(parts):
        for line in part:
            output_str += line
        if idx == len(parts) - 1:
            break
        if new_replacement:
            output_str += new_replacement[idx]
        else:
            output_str += replacement

    return output_str


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
    with open(filepath, "r", encoding = "UTF-8") as infile:
        lines = infile.readlines()
    return lines


def _write_file(filepath: str, lines: str):
    """
    Writes the contents of a string to a file, overwriting its original contents
    """
    with open(filepath, "w", encoding = "UTF-8") as outfile:
        outfile.write(lines)
