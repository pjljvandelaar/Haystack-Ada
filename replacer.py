import libadalang as lal
from typing import Optional, Union
from searchresult import SearchResult
from location import Location


class Replacer:
    def __init__(self, filename: str, slocs: list, replacement: str, indexes: Optional[Union[list, None]] = None, output: Optional[Union[str, None]] = None):
        """Constructor method
        """
        self.slocs = slocs
        self.replacement = replacement
        self.filename = filename
        self.locations = self.parse_sloc()
        self.indexes = [i for i in range(len(self.locations))] if indexes is None else indexes
        self.output = filename if output is None else output

    def parse_sloc(self):
        locations = []
        for sloc in self.slocs:
            range = str(sloc).split("-")
            [line1, pos1], [line2, pos2] = range[0].split(":"), range[1].split(":")
            locations.append(Location(int(line1), int(line2), int(pos1), int(pos2)))
        return locations

    def replace(self) -> None:
        with open(self.filename, "r") as infile:
            lines = infile.readlines()
        parts = []
        for i, j in enumerate(self.indexes):
            start_line = self.locations[j].start_line
            end_line = self.locations[j].end_line
            start_char = self.locations[j].start_char
            end_char = self.locations[j].end_char
            if i == 0:
                parts.append(lines[:start_line-1])
                parts[-1].append(lines[start_line-1][:start_char-1])
            else:
                previous_end_line = self.locations[self.indexes[i - 1]].end_line
                previous_end_char = self.locations[self.indexes[i - 1]].end_char
                parts.append([lines[previous_end_line - 1][previous_end_char - 1:]])
                parts[-1].extend(lines[previous_end_line:start_line - 1])
                parts[-1].append(lines[start_line - 1][:start_char - 1])
            if i == len(self.indexes) - 1:
                parts.append([lines[end_line-1][end_char - 1:]])
                parts[-1].extend(lines[end_line:])
        print(*parts, sep='\n')
        output_str = ""
        for idx, part in enumerate(parts):
            for line in part:
                output_str += line
            if idx == len(parts) - 1:
                break
            output_str += self.replacement

        with open(self.output, "w") as outfile:
            outfile.write(output_str)


res = SearchResult("hello.adb", "Put_Line (\"Hello, World!\")",
                       rule=lal.GrammarRule.expr_rule)
test = Replacer(res.filename, res.locations, "test!", output="replacer_test.adb")
test.replace()
