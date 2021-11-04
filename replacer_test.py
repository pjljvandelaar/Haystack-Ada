import unittest
from searchresult import SearchResult
from replacer import Replacer
import libadalang as lal


class TestReplacer(unittest.TestCase):
    def setUp(self) -> None:
        self.output = "replacer_test.adb"

    def test_one_to_one(self):
        filename = "dosort.adb"
        replacement = "Put(\"Hello world\")"
        # standard put statement
        dosort1 = SearchResult(filename, "Put(Arr(I).X)", rule=lal.GrammarRule.expr_rule)
        dosort1_replace = Replacer(filename, dosort1.locations, replacement, output=self.output)
        # self.assertEqual(dosort1.found, True)
        # self.assertEqual(str(dosort1.locations), "[<SlocRange 34:10-34:23>]")
        dosort1_replace.replace()
        with open(filename) as f:
            lines_in = [line.strip() for line in f]
        with open(self.output) as f:
            lines_out = [line.strip() for line in f]
        for i, line in enumerate(lines_out):
            if i is not 33:
                self.assertTrue(lines_in[i] == lines_out[i])
            else:
                self.assertEqual(lines_out[i], "Put(\"Hello world\");")

    def test_one_to_many(self):
        # standard put statement
        stack1 = SearchResult("g_stack_user.adb", "Put_Line(\"Something unexpected went wrong\")",
                              rule=lal.GrammarRule.expr_rule)
        stack1_replace = Replacer("g_stack_user.adb", stack1.locations, "for I     in Arr'Range loop\n\n"
                                                                        "Put(Arr(I).X);\n"
                                                                        "Put(Arr(I).Y);\n"
                                                                        "Put(\"Contrary to popular belief, Lorem Ipsum is not simply random text\");\n"
                                                                        "end loop;\",", output=self.output)
        stack1_replace.replace()

    def test_many_to_many(self):
        # for loop
        dosort2 = SearchResult("dosort.adb", "for I     in Arr'Range loop\n\n"
                                             "Put(\"(\") ;\n"
                                             "Put(Arr(I).X);\n"
                                             "Put(\",\");\n"
                                             "Put(Arr(I).Y);  \n"
                                             "Put(\")\");\n\n\n"
                                             "end loop;\",", rule=lal.GrammarRule.loop_stmt_rule)
        dosort1_replace = Replacer("dosort.adb", dosort2.locations, "for I in array123'Range loop\n\n"
                                                                    "when Data_Error =>\n"
                                                                    "Put_Line(\"Lorem ipsum.\");\n"
                                                                    "Put(\",\");\n"
                                                                    "Put_Line(\"Dolor sit amet.\");\n"
                                                                    "end loop;\",", output=self.output)
        # self.assertEqual(dosort2.found, True)
        # self.assertEqual(str(dosort2.locations), "[<SlocRange 32:7-38:16>]")

    def test_empty(self):
        # not found
        dosort3 = SearchResult("dosort.adb", "Put_Line(\"Lorem ipsum.\")", rule=lal.GrammarRule.expr_rule)
        dosort3_replace = Replacer("dosort.adb", dosort3.locations, "Put(\"Hello world\")", output=self.output)
        # self.assertEqual(dosort3.found, False)
        # self.assertEqual(str(dosort3.locations), "[]")
        dosort3_replace.replace()

    def test_erase(self):
        # exception rule
        stack2 = SearchResult("g_stack_user.adb", "when Data_Error =>\n"
                                                  "Put_Line(\"Okay, that'll be your first string.\");\n",
                              rule=lal.GrammarRule.exception_handler_rule)
        # self.assertEqual(stack2.found, True)
        stack2_replace = Replacer("stack2.adb", stack2.locations, "", output=self.output)
        stack2_replace.replace()
