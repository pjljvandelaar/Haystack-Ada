import libadalang as lal
from typing import Optional


class SearchResult:
    """Class used for searching a text in a file and storing its location.

    :param filename: Name of the file to be searched
    :type filename: str
    :param fragment: Piece of text to be searched for
    :type fragment: str
    :param rule: Grammar rule used to parse the fragment
    :type rule: class:'libadalang.GrammarRule', optional
    """

    def __init__(self, filename: str, fragment: str, rule: Optional[lal.GrammarRule] = lal.default_grammar_rule):
        """Constructor method
        """
        self.diagnostics = []
        self.locations = []
        self.rule = rule
        self.filename = filename
        self.file_tree = self.analyze()
        self.fragment = fragment
        self.fragment_tree = self.analyze(fragment=True)
        self.last_location = None
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
        if not root1.children and not root2.children and root1.text != root2.text:
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
        if tree is None:
            return False
        if self.are_identical(tree, subtree):
            return True
        for child in tree.children:
            if self.is_subtree(child, subtree):
                self.locations.append(self.last_location)
        return False

    def analyze(self, fragment: Optional[bool] = False) -> lal.AnalysisUnit:
        """
        Creates a tree from text fragment

        :param fragment: whether the analyzed input is a fragment
        :type fragment: bool, optional
        :return: An analysis unit containing the tree
        :rtype: class:'libadalang.AnalysisUnit'
        """
        context = lal.AnalysisContext()
        if fragment:
            unit = context.get_from_buffer("", self.fragment, rule=self.rule)
        else:
            unit = context.get_from_file(self.filename)
        if unit.diagnostics:
            for d in unit.diagnostics:
                print(d)
            self.diagnostics.extend(unit.diagnostics)
            raise ValueError
        else:
            return unit


'''
res = SearchResult("calc.adb", "Put(\"test1\")", rule=lal.GrammarRule.expr_rule)
print(res.found)
print(res.locations)

res = SearchResult("calc.adb", "Put(\"test2\")", rule=lal.GrammarRule.expr_rule)
print(res.found)
print(res.locations)
'''