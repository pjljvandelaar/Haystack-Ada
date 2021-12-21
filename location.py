"""
This module defines the Location data structure.
"""
from typing import Dict
import libadalang as lal # type: ignore


class Location:
    """
    This class stores data about pattern matches, namely where they start, where they end,
    and if any wildcards were used in the match.
    If wildcards were used, it stores what text matched to the wildcard,
    so that this can later be backreferenced in the replacement.
    """
    start_line: int
    end_line: int
    start_char: int
    end_char: int
    wildcards: Dict[str, lal.AdaNode]

    def __init__(
        self,
        start_line: int,
        end_line: int,
        start_char: int,
        end_char: int,
        wildcards: Dict[str, lal.AdaNode],
    ):
        self.start_line = start_line
        self.end_line = end_line
        self.start_char = start_char
        self.end_char = end_char
        self.wildcards = wildcards

    def __repr__(self) -> str:
        return (
            str(self.start_line)
            + ":"
            + str(self.start_char)
            + "-"
            + str(self.end_line)
            + ":"
            + str(self.end_char)
        )
