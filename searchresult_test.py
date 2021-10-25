import unittest
from searchresult import SearchResult
import libadalang as lal


class TestSearchResult(unittest.TestCase):
    def test_expr_rule(self):
        # standard put statement
        dosort1 = SearchResult("dosort.adb", "Put(Arr(I).X)", rule=lal.GrammarRule.expr_rule)
        self.assertEqual(dosort1.found, True)
        self.assertEqual(str(dosort1.locations), "[<SlocRange 34:10-34:23>]")

    def test_for_loop(self):
        # for loop
        dosort2 = SearchResult("dosort.adb", "for I     in Arr'Range loop\n\n"
                                             "Put(\"(\") ;\n"
                                             "Put(Arr(I).X);\n"
                                             "Put(\",\");\n"
                                             "Put(Arr(I).Y);  \n"
                                             "Put(\")\");\n\n\n"
                                             "end loop;\",",
                               rule=lal.GrammarRule.loop_stmt_rule)
        self.assertEqual(dosort2.found, True)
        self.assertEqual(str(dosort2.locations), "[<SlocRange 32:7-38:16>]")

    def test_empty(self):
        # empty search term
        dosort3 = SearchResult("dosort.adb", "",
                               rule=lal.GrammarRule.compilation_rule)
        self.assertEqual(dosort3.found, False)
        self.assertEqual(str(dosort3.locations), "[]")

    def test_invalid_file(self):
        # invalid filename
        with self.assertRaises(ValueError):
            SearchResult("", "", rule=lal.GrammarRule.compilation_rule)

    def test_exception_file(self):
        # exception rule
        stack1 = SearchResult("g_stack_user.adb", "when Data_Error =>\n"
                                                  "Put_Line(\"Okay, that'll be your first string.\");\n",
                              rule=lal.GrammarRule.exception_handler_rule)
        self.assertEqual(stack1.found, True)

    def test_if(self):
        # if statement
        obj1 = SearchResult("obj1.adb", "if LC.Count > L\n"
                                        "then LC.Count := L;\n"
                                        "end if;",
                            rule=lal.GrammarRule.if_stmt_rule)
        self.assertEqual(obj1.found, True)
        self.assertEqual(str(obj1.locations), "[<SlocRange 38:7-38:50>]")
