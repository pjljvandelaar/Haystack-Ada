import libadalang as lal
from typing import Optional, Union
from searchresult import SearchResult


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
            locations.append(((line1, pos1), (line2, pos2)))
        return locations

    def replace(self) -> None:
        with open(self.filename, "r") as infile:
            lines = infile.readlines()
        parts = []
        for i, j in enumerate(self.indexes):
            start_line = int(self.locations[j][0][0])
            end_line = int(self.locations[j][1][0])
            start_char = int(self.locations[j][0][1])
            end_char = int(self.locations[j][1][1])
            if i == 0:
                parts.append(lines[:start_line-1])
                parts[-1].append(lines[start_line-1][:start_char-1])
            else:
                previous_end_line = int(self.locations[self.indexes[i - 1]][1][0])
                previous_end_char = int(self.locations[self.indexes[i - 1]][1][1])
                parts.append([lines[previous_end_line - 1][previous_end_char:]])
                parts[-1].extend(lines[previous_end_line:start_line - 1])
                parts[-1].append(lines[start_line - 1][:start_char - 1])
            if i == len(self.indexes) - 1:
                parts.append([lines[end_line-1][end_char:]])
                parts[-1].extend(lines[end_line:])
        output_str = ""
        for idx, part in enumerate(parts):
            for line in part:
                output_str += line
            if idx == len(parts) - 1:
                break
            output_str += self.replacement
        print(len(parts))
        print(*parts, sep='\n')
        with open(self.output, "w") as outfile:
            outfile.write(output_str)
        '''
            print(self.locations[i])

            # print(linestart,linend)
            # Equals line:
            if linestart == linend:
                startChar = int(self.locations[i][0][1])
                endChar = int(self.locations[i][1][1])
                replacer.replace_line(self.filename,linestart,startChar,self.replacement,endChar, output=self.output)
            # No equals line (ex: for loop...)
            elif linestart != linend:
                startChar = int(self.locations[i][0][1])
                replacer.replace_body(self.filename,linestart,linend,["Put_Line(firstLine);\n","Put_Line(secondLine);\n","Put_Line(thirdLine);\n"],startChar, output=self.output)
        # print("Out of the loop")
        '''

'''
res = SearchResult("hello.adb", "Put(Arr(I).X)", rule=lal.GrammarRule.expr_rule)
# res = SearchResult("hello.adb", "\"Hello World\"", rule=lal.GrammarRule.expr_rule)
res = SearchResult("hello.adb", "if The_Month > The_Time then\n"
                                        "The_Month := The_Time;\n"
                                        "end if;",
                              rule=lal.GrammarRule.if_stmt_rule)

test = Replacer(res.filename, res.locations, "test")
test.replace()
'''
res = SearchResult("dosort.adb", "for I     in Arr'Range loop\n\n"
                                     "Put(\"(\") ;\n"
                                     "Put($array);\n"
                                     "Put(\",\");\n"
                                     "Put(Arr(I).Y);  \n"
                                     "Put(\")\");\n\n\n"
                                     "end loop;\",",
                       rule=lal.GrammarRule.loop_stmt_rule)
test = Replacer(res.filename, res.locations, "test1!\ntest2!\nworks?\n", output="replacer_test.adb")
test.replace()
