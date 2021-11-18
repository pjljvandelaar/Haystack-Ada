import libadalang as lal # type: ignore
from typing import Optional, List
from location import Location

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
    found: bool

    def __init__(self, filename: str, fragment: str, rule: Optional[lal.GrammarRule] = lal.default_grammar_rule,
                 case_insensitive: Optional[bool] = False):
        """Constructor method
        """
        self.locations = []
        self.file_tree = self.analyze_file(filename)
        self.fragment_tree = self.analyze_fragment(fragment, rule)
        self.last_location = ""
        self.case_insensitive = case_insensitive
        self.is_subtree(self.file_tree.root, self.fragment_tree.root)
        self.found = bool(self.locations)

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
        if root1 is None or root2 is None or len(root1.children) != len(root2.children):
            return False
        if not root1.children and not root2.children and not text_comparison(root1.text, root2.text, self.case_insensitive):
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
        return False

    def analyze_fragment(self, fragment: str, rule: Optional[lal.GrammarRule]) -> lal.AnalysisUnit:
        """
        Creates a tree from text fragment

        :return: An analysis unit containing the tree
        """
        rules = lal.GrammarRule._c_to_py[::-1]
        rules.insert(0, rules.pop(rules.index(str(rule))))
        for idx, rule in enumerate(rules):
            if idx != 0:
                print(rules[idx - 1], "failed, retrying with", rule)
            context = lal.AnalysisContext()
            unit = context.get_from_buffer("", fragment, rule=getattr(lal.GrammarRule, rule))
            if not unit.diagnostics:
                return unit
        for d in unit.diagnostics:
            print(d)
        raise ValueError
    
    def analyze_file(self, filename: str) -> lal.AnalysisUnit:
        """
        Creates a tree from ada file

        :return: An analysis unit containing the tree
        """
        context = lal.AnalysisContext()
        unit = context.get_from_file(filename)
        if not unit.diagnostics:
            return unit
        for d in unit.diagnostics:
            print(d)
        raise ValueError

    def parse_sloc(self, sloc: str) -> Location:
        """Transforms sloc into Location type element

        :return: Location representing the input sloc
        """
        range_ = str(sloc).split("-")
        [line1, pos1], [line2, pos2] = range_[0].split(":"), range_[1].split(":")
        return Location(int(line1), int(line2), int(pos1), int(pos2))


def text_comparison(text1, text2, case_insensitive):
    return text1 == text2 if not case_insensitive else text1.lower() == text2.lower()