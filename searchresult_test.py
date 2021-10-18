import unittest
from searchresult import SearchResult
import libadalang as lal


class TestSearchResult(unittest.TestCase):
    def test_result(self):
        # standard put statement
        dosort1 = SearchResult("dosort.adb", "Put(Arr(I).X)", rule=lal.GrammarRule.expr_rule)
        self.assertEqual(dosort1.found, True)
        self.assertEqual(str(dosort1.locations), "[<SlocRange 34:10-34:23>]")

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

        # empty search term
        dosort3 = SearchResult("dosort.adb", "",
                               rule=lal.GrammarRule.compilation_rule)
        self.assertEqual(dosort3.found, False)
        self.assertEqual(str(dosort3.locations), "[]")

        # invalid filename
        with self.assertRaises(ValueError):
            SearchResult("", "", rule=lal.GrammarRule.compilation_rule)

        # exception rule
        stack1 = SearchResult("g_stack_user.adb", "when Data_Error =>\n"
                                                  "Put_Line(\"Okay, that'll be your first string.\");\n",
                              rule=lal.GrammarRule.exception_handler_rule)
        self.assertEqual(stack1.found, True)

        # if statement
        obj1 = SearchResult("obj1.adb", "if LC.Count > L\n"
                                        "then LC.Count := L;\n"
                                        "end if;",
                              rule=lal.GrammarRule.if_stmt_rule)
        self.assertEqual(obj1.found, True)
        self.assertEqual(str(obj1.locations), "[<SlocRange 38:7-38:50>]")
