import libadalang as lal
from typing import Optional, Union
from searchresult import SearchResult
import ReplaceMain as replacer


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
            linestart = int(self.locations[i][0][0])
            linend = int(self.locations[i][1][0])
            # print(linestart,linend)
            # Equals line:
            if(linestart == linend):
                startChar = int(self.locations[i][0][1])
                endChar = int(self.locations[i][1][1])
                replacer.replace_line(self.filename,linestart,startChar,"I Test Replacer!",endChar)
            # No equals line (ex: for loop...)
            elif(linestart != linend):
                startChar = int(self.locations[i][0][1])
                replacer.replace_body(self.filename,linestart,linend,["Put_Line(firstLine);\n","Put_Line(secondLine);\n","Put_Line(thirdLine);\n"],startChar)
        print("Out of the loop")


res = SearchResult("hello.adb", "Put(Arr(I).X)", rule=lal.GrammarRule.expr_rule)
# res = SearchResult("hello.adb", "\"Hello World\"", rule=lal.GrammarRule.expr_rule)
'''res = SearchResult("hello.adb", "if The_Month > The_Time then\n"
                                        "The_Month := The_Time;\n"
                                        "end if;",
                              rule=lal.GrammarRule.if_stmt_rule)
'''
test = Replacer(res.filename, res.locations, "test")
test.replace()

