import libadalang as lal
from typing import Optional, Union
from searchresult import SearchResult


class Replacer:
    def __init__(self, filename: str, slocs: list, replacement: str, indexes: Optional[Union[list, None]] = None):
        """Constructor method
        """
        self.slocs = slocs
        self.replacement = replacement
        self.filename = filename
        self.locations = self.parse_sloc()
        if indexes is None:
            self.indexes = [i for i in range(len(self.locations))]
        else:
            self.indexes = indexes

    def parse_sloc(self):
        locations = []
        for sloc in self.slocs:
            range = str(sloc).split("-")
            [line1, pos1], [line2, pos2] = range[0].split(":"), range[1].split(":")
            locations.append(((line1, pos1), (line2, pos2)))
        return locations

    def replace(self) -> None:
        for i in self.indexes[::-1]:
            print(self.locations[i])
            # TODO implement replacing the file at self.locations[i]
            pass


res = SearchResult("put_test.adb", "Put(Arr(I).X)", rule=lal.GrammarRule.expr_rule)
test = Replacer(res.filename, res.locations, "test")
test.replace()
