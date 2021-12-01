import libadalang as lal # type: ignore
from typing import Optional, List
from location import Location
import GPS


class SearchResult:
    """Class used for searching a text in a file and storing its location.

    :param filename: Name of the file to be searched
    :type filename: str
    :param fragment: Piece of text to be searched for
    :type fragment: str
    :param rule: Grammar rule used to parse the fragment
    :type rule: class:'libadalang.GrammarRule', optional
    """

    locations: List[Location]
    file_tree: lal.AnalysisUnit
    fragment_tree: lal.AnalysisUnit
    last_location: str
    case_insensitive: Optional[bool]

    def __init__(self, filename: str, fragment: str, rule: lal.GrammarRule = lal.default_grammar_rule, case_insensitive: Optional[bool] = False):
        """Constructor method
        """
        self.locations = []
        self.wildcards = {}
        self.rule = rule
        self.filename = filename
        self.file_tree = self.analyze()
        self.fragment = fragment
        self.fragment_tree = self.analyze(fragment=True)
        self.last_location = None
        self.case_insensitive = case_insensitive
        self.analyze_file(filename)
        if not self.analyze_fragment(fragment, rule):
            choice = GPS.MDI.combo_selection_dialog("Try other rules?", "Rule " + str(rule) + " did not parse your search query, should we try other parse rules?", ["Yes", "No"])
            if choice == "Yes":
                self.analyze_fragment_try_rules(fragment)
            else:
                parse_failure()
        self.is_subtree(self.file_tree.root, self.fragment_tree.root)

    def are_identical(self, root1, root2) -> bool:
        """
        Checks whether leaves of two tree roots are identical

        :param root1: Root of the first tree to be compared
        :param root2: Root of the second  tree to be compared
        :return: True if the children are identical
        :rtype: bool
        """
        if root1 is None and root2 is None:
            return True
        if root1 is None or root2 is None:
            return False
        if not root2.children and root2.text and root2.text[0] == '$' and self.wild_comparison(root1, root2):
            # save the underlying text in the dictionary
            # print(root1.text, root1.__class__, inspect.getmro(type(root1)))
            return True
        if len(root1.children) != len(root2.children):
            return False
        if not root1.children and not root2.children and not self.text_comparison(root1, root2):
            return False
        for i in range(len(root1.children)):
            if not self.are_identical(root1.children[i], root2.children[i]):
                return False
        self.last_location = root1.sloc_range
        return True

    def is_subtree(self, tree, subtree) -> bool:
        """
        Checks whether one tree is a subtree of another tree

        :param tree: The tree to be searched
        :param subtree: The tree to be searched for
        :return: True if subtree exists in the tree
        :rtype: bool
        """
        if subtree is None:
            return True
        if tree is None or not subtree.children:
            return False
        if self.are_identical(tree, subtree):
            return True
        for child in tree.children:
            if self.is_subtree(child, subtree):
                self.locations.append(self.parse_sloc(self.last_location))
        self.wildcards = {}
        return False

    def analyze_fragment(self, fragment:str, rule: lal.GrammarRule) -> bool:
        context = lal.AnalysisContext()
        unit = context.get_from_buffer("", fragment, rule=getattr(lal.GrammarRule, rule))
        if not unit.diagnostics:
            self.fragment_tree = unit
            return True
        return False

    def analyze_fragment_try_rules(self, fragment: str):
        """
        Creates a tree from text fragment

        :return: An analysis unit containing the tree
        """
        rules = lal.GrammarRule._c_to_py
        for idx, rule in enumerate(rules):
            if idx != 0:
                print(rules[idx - 1], "failed, retrying with", rule)
            if self.analyze_fragment(fragment, rule):
                print("Succeeded with", rule)
                return
        parse_failure()

    def analyze_file(self, filename: str):
        """
        Creates a tree from ada file

        :return: An analysis unit containing the tree
        """
        context = lal.AnalysisContext()
        unit = context.get_from_file(filename)
        if not unit.diagnostics:
            self.file_tree = unit
            return
        for d in unit.diagnostics:
            print(d)
        raise ValueError

    def parse_sloc(self, sloc: str) -> Location:
        """Transforms sloc into Location type element

        :return: Location representing the input sloc
        """
        range_ = str(sloc).split("-")
        [line1, pos1], [line2, pos2] = range_[0].split(":"), range_[1].split(":")
        return Location(int(line1), int(line2), int(pos1), int(pos2), self.wildcards)

    def wild_comparison(self, root1, root2):
        '''
        print(root1.text, root1.__class__, inspect.getmro(type(root1)))
        return str(root1.__class__) in ["<class 'libadalang." + i + "'>" for i in self.wildcards[root2.text]]
        '''
        if root2.text not in self.wildcards:
            self.wildcards[root2.text] = root1.text
        elif self.wildcards[root2.text] != root1.text:
            return False
        return True

    def text_comparison(self, root1, root2):
        return root1.text == root2.text if not self.case_insensitive else root1.text.lower() == root2.text.lower()

def parse_failure():
    GPS.MDI.dialog("Search query couldn't be parsed :(")
    raise ValueError
      
fragments = ["$S_var : $S_type;\n $S_var : $S_type;",  # same var, same type
             "$S_var1 : $S_type;\n $S_var2 : $S_type;",  # same type
             "$S_var : $S_type1;\n $S_var : $S_type2;",  # same var
             "$S_var1 : $S_type1;\n $S_var2 : $S_type2;"]  # any

for fragment in fragments:
    wildcard = SearchResult("test_programs/wildcards_tests.adb", fragment, rule=lal.GrammarRule.recov_decl_part_rule)
    print(wildcard.found, wildcard.locations)

    for location in wildcard.locations:
        # print(location.wildcards)
        pass
