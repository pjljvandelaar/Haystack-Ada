from typing import Dict


class Location:
    start_line: int
    end_line: int
    start_char: int
    end_char: int
    wildcards: Dict[str, str]

    def __init__(self, start_line: int, end_line: int, start_char: int, end_char: int, wildcards: Dict[str, str]):
        self.start_line = start_line
        self.end_line = end_line
        self.start_char = start_char
        self.end_char = end_char
        self.wildcards = wildcards

    def __repr__(self) -> str:
        return str(self.start_line) + ":" + str(self.start_char) + "-" \
            + str(self.end_line) + ":" + str(self.end_char)
